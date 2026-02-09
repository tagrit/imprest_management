"""
FIXED ACCOUNTING ENTRIES - imprest_request.py
CRITICAL FIX: Cash/Bank now DEBITED (reduced) on disbursement
"""

import frappe
from frappe.model.document import Document
from frappe.utils import (
    getdate, nowdate, now, get_datetime, 
    formatdate, flt, cint, validate_email_address, add_days
)
from frappe import _
import json


class ImprestRequest(Document):
    def validate(self):
        """Validation before saving"""
        self.calculate_totals()
        
        if not self.expense_items:
            frappe.throw(_("Please add at least one expense item"))
        
        if self.workflow_state == "Approved" and self.approved_amount:
            if flt(self.approved_amount) > flt(self.total_requested_amount):
                frappe.throw(_("Approved amount cannot exceed requested amount"))
        
        # VALIDATION: Check reconciliation doesn't exceed approved amount
        if self.reconciliation_items and self.approved_amount:
            self.validate_reconciliation_amount()
        
        if self.employee and not self.employee_name:
            self.employee_name = frappe.db.get_value("Employee", self.employee, "employee_name")
        
        self.title = f"{self.employee_name or self.employee} - {formatdate(self.posting_date)}"
        
    
    def validate_reconciliation_amount(self):
        """
        VALIDATION: Ensure reconciliation items don't exceed approved amount
        """
        total_reconciliation = 0
        for item in self.reconciliation_items:
            total_reconciliation += flt(item.amount, 2)
        
        approved = flt(self.approved_amount, 2)
        
        # Allow small rounding differences (1 unit of currency)
        if total_reconciliation > (approved + 1.0):
            frappe.throw(_(
                "Total reconciliation amount ({0}) exceeds approved amount ({1}). "
                "Please adjust reconciliation items or request additional approval."
            ).format(
                frappe.format_value(total_reconciliation, {'fieldtype': 'Currency'}),
                frappe.format_value(approved, {'fieldtype': 'Currency'})
            ))
        
        # Warning if very close to limit
        if total_reconciliation > (approved - 50) and total_reconciliation <= approved:
            frappe.msgprint(_(
                "⚠️ Warning: Reconciliation amount ({0}) is very close to approved limit ({1})"
            ).format(
                frappe.format_value(total_reconciliation, {'fieldtype': 'Currency'}),
                frappe.format_value(approved, {'fieldtype': 'Currency'})
            ), indicator='orange', alert=True)
            
            
    def onload(self):
        """Set defaults when form loads"""
        if self.is_new():
            if not self.source_account:
                try:
                    if frappe.db.exists("Imprest Management Settings", "Imprest Management Settings"):
                        settings = frappe.get_single("Imprest Management Settings")
                        if settings.default_source_account:
                            self.source_account = settings.default_source_account
                except Exception:
                    pass
                    
    
    def calculate_totals(self):
        """Calculate total requested amount from expense items"""
        total = 0
        for item in self.expense_items:
            item.amount = flt(item.quantity, 2) * flt(item.rate, 2)
            total += flt(item.amount, 2)
        
        self.total_requested_amount = flt(total, 2)
        
        if not self.approved_amount:
            self.approved_amount = self.total_requested_amount
    
    def on_update(self):
        """After save actions"""
        if self.workflow_state == "Approved" and not self.accounting_entry_created:
            self.create_disbursement_entry()
        
        if self.workflow_state == "Rejected" and self.accounting_entry_created:
            self.reverse_accounting_entries()
    
    def create_disbursement_entry(self):
        """
        Create Journal Entry for disbursement
        
        CORRECT ACCOUNTING FOR IMPREST DISBURSEMENT:
        When giving cash to employee as advance/imprest:
        Dr. Employee Advance (ASSET INCREASES - employee now has our money/owes us)
        Cr. Cash/Bank Account (ASSET DECREASES - money goes out)
        
        Employee Advance is an ASSET (receivable from employee)
        """
        if not self.approved_amount or self.approved_amount <= 0:
            frappe.throw(_("Cannot create disbursement entry without approved amount"))
            
        if not self.source_account:
            frappe.throw(_("Source Account is required"))
  
        employee_account = self.get_employee_advance_account()
        
        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Bank Entry"
        je.posting_date = self.approval_date or nowdate()
        je.company = self.company
        je.user_remark = f"Imprest disbursement for {self.name} - {self.purpose}"
        je.imprest_request = self.name
        je.cheque_no = self.name 
        je.cheque_date = self.approval_date or nowdate() 
        
        # ENTRY 1: Debit Employee Advance (ASSET INCREASES - employee has our money)
        je.append("accounts", {
            "account": employee_account,
            "debit_in_account_currency": flt(self.approved_amount, 2),
            "credit_in_account_currency": 0,
            "party_type": "Employee",
            "party": self.employee
        })
        
        # ENTRY 2: Credit Cash/Bank (ASSET DECREASES - money OUT)
        je.append("accounts", {
            "account": self.source_account,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": flt(self.approved_amount, 2)
        })
        
        je.flags.ignore_permissions = True
        je.insert()
        je.submit()
        
        self.db_set("disbursement_journal_entry", je.name)
        self.db_set("accounting_entry_created", 1)
        self.db_set("disbursement_date", je.posting_date)
        
        if self.docstatus == 0:
            self.submit()
            frappe.db.commit()
        
        self.auto_populate_reconciliation_items()
        self.send_approval_notification()
        
        frappe.msgprint(_("Disbursement entry {0} created successfully. Cash reduced by {1}").format(
            je.name, 
            frappe.format_value(self.approved_amount, {'fieldtype': 'Currency'})
        ))

    
    def get_employee_advance_account(self):
        """Get or create employee-specific advance account"""
        existing_account = frappe.db.sql("""
            SELECT name 
            FROM `tabAccount` 
            WHERE account_name LIKE %s 
            AND company = %s 
            AND parent_account IS NOT NULL
            LIMIT 1
        """, (f"{self.employee_name} - Advance%", self.company), as_dict=1)
        
        if existing_account:
            return existing_account[0].name
        
        settings = frappe.get_doc("Imprest Management Settings")
        if not settings.employee_advance_parent_account:
            frappe.throw(_("Please set Employee Advance Parent Account in Settings"))
        
        try:
            account = frappe.new_doc("Account")
            account.account_name = f"{self.employee_name} - Advance"
            account.parent_account = settings.employee_advance_parent_account
            account.company = self.company
            account.account_currency = frappe.db.get_value("Company", self.company, "default_currency")
            account.flags.ignore_permissions = True
            account.insert()
            
            return account.name
        except frappe.DuplicateEntryError:
            existing_account = frappe.db.sql("""
                SELECT name 
                FROM `tabAccount` 
                WHERE account_name LIKE %s 
                AND company = %s 
                AND parent_account IS NOT NULL
                LIMIT 1
            """, (f"{self.employee_name} - Advance%", self.company), as_dict=1)
            
            if existing_account:
                return existing_account[0].name
            else:
                frappe.throw(_("Failed to create or find employee advance account"))
    
    def reverse_accounting_entries(self):
        """Reverse disbursement if rejected"""
        if not self.disbursement_journal_entry:
            return
        
        original_je = frappe.get_doc("Journal Entry", self.disbursement_journal_entry)
        
        reversal_je = frappe.new_doc("Journal Entry")
        reversal_je.voucher_type = "Journal Entry"
        reversal_je.posting_date = nowdate()
        reversal_je.company = self.company
        reversal_je.user_remark = f"Reversal of imprest {self.name} due to rejection"
        
        for account in original_je.accounts:
            reversal_je.append("accounts", {
                "account": account.account,
                "debit_in_account_currency": account.credit_in_account_currency,
                "credit_in_account_currency": account.debit_in_account_currency,
            })
        
        reversal_je.flags.ignore_permissions = True
        reversal_je.insert()
        reversal_je.submit()
        
        self.db_set("reversal_journal_entry", reversal_je.name)
        frappe.msgprint(_("Reversal entry {0} created").format(reversal_je.name))
    
    def on_submit(self):
        """On submit actions"""
        pass
    
    def auto_populate_reconciliation_items(self):
        """Auto-populate reconciliation items from expense items"""
        if self.reconciliation_items:
            return
        
        if self.workflow_state != "Approved":
            return
        
        for expense_item in self.expense_items:
            self.append("reconciliation_items", {
                "expense_category": expense_item.expense_category,
                "description": expense_item.description,
                "amount": expense_item.amount,
                "reconciliation_status": "Pending",
                "quantity": expense_item.quantity,
                "rate": expense_item.rate
            })
        
        frappe.db.commit()
        frappe.msgprint(_("Reconciliation items auto-populated from expense items. You can edit amounts before submitting."))
    
    def send_approval_notification(self):
        """Send email notification"""
        if not self.employee:
            return
        
        employee_email = frappe.db.get_value("Employee", self.employee, "user_id")
        if not employee_email:
            return
        
        message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #4CAF50;">✓ Imprest Request Approved!</h2>
            
            <p>Dear {self.employee_name},</p>
            
            <p>Your imprest request <strong>{self.name}</strong> has been approved.</p>
            
            <div style="background-color: #e8f5e9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0;"><strong>Approved Amount:</strong> {frappe.format_value(self.approved_amount, {'fieldtype': 'Currency'})}</p>
                <p style="margin: 10px 0 0 0;"><strong>Purpose:</strong> {self.purpose}</p>
                {f'<p style="margin: 10px 0 0 0;"><strong>Event:</strong> {self.event}</p>' if self.event else ''}
            </div>
            
            <p>Please attach receipts and submit for review. Note: Total reconciliation amount cannot exceed the approved amount.</p>
            
            <p>Best regards,<br>Finance Team</p>
        </div>
        """
        
        frappe.sendmail(
            recipients=[employee_email],
            subject=f"Imprest Request {self.name} Approved",
            message=message
        )


# ============================================================================
# RECONCILIATION FUNCTIONS
# ============================================================================

@frappe.whitelist()
def submit_reconciliation(imprest_request):
    """Employee submits reconciliation"""
    doc = frappe.get_doc("Imprest Request", imprest_request)
    
    if doc.workflow_state != "Approved":
        frappe.throw(_("Only approved imprest can be reconciled"))
    
    new_items = [item for item in doc.reconciliation_items 
                 if item.reconciliation_status == "Pending"]
    
    if not new_items:
        frappe.throw(_("No new reconciliation items to submit"))
    
    new_items_total = sum(flt(item.amount) for item in new_items)
    
    # VALIDATION: Check if submission would exceed approved amount
    total_reconciled = flt(doc.total_reconciled_amount or 0)
    total_after_submission = total_reconciled + new_items_total
    
    if total_after_submission > flt(doc.approved_amount):
        frappe.throw(_(
            "Cannot submit: Total would be {0}, which exceeds approved amount of {1}. "
            "Please reduce reconciliation amounts or request additional approval."
        ).format(
            frappe.format_value(total_after_submission, {'fieldtype': 'Currency'}),
            frappe.format_value(doc.approved_amount, {'fieldtype': 'Currency'})
        ))
    
    if not doc.reconciliation_status or doc.reconciliation_status == "Draft":
        doc.db_set("reconciliation_status", "Pending Review")
    
    if not doc.reconciliation_submitted_date:
        doc.db_set("reconciliation_submitted_date", now())
    
    variance = flt(doc.approved_amount) - total_reconciled
    doc.db_set("variance_amount", variance)
    
    notify_finance_team_for_reconciliation(doc, new_items_total, len(new_items))
    
    frappe.msgprint(_(
        "Submitted {0} receipt(s) totaling {1}"
    ).format(len(new_items), frappe.format_value(new_items_total, {'fieldtype': 'Currency'})))
    
    return {"success": True}


@frappe.whitelist()
def approve_reconciliation_items(imprest_request, item_names):
    """Finance approves specific items"""
    doc = frappe.get_doc("Imprest Request", imprest_request)
    
    if not item_names:
        frappe.throw(_("Select at least one item"))
    
    if isinstance(item_names, str):
        item_names = json.loads(item_names)
    
    items_to_approve = []
    for item in doc.reconciliation_items:
        if item.name in item_names:
            items_to_approve.append(item)
    
    if not items_to_approve:
        frappe.throw(_("No valid items found"))
    
    # VALIDATION: Check if approval would exceed approved amount
    current_approved = flt(doc.total_reconciled_amount or 0)
    additional_amount = sum(flt(item.amount) for item in items_to_approve)
    total_after_approval = current_approved + additional_amount
    
    if total_after_approval > flt(doc.approved_amount):
        frappe.throw(_(
            "Cannot approve: Total would be {0}, which exceeds approved amount of {1}"
        ).format(
            frappe.format_value(total_after_approval, {'fieldtype': 'Currency'}),
            frappe.format_value(doc.approved_amount, {'fieldtype': 'Currency'})
        ))
    
    # Mark as approved
    for item in items_to_approve:
        frappe.db.set_value("Reconciliation Item", item.name, "reconciliation_status", "Approved")
        frappe.db.set_value("Reconciliation Item", item.name, "approved_date", now())
        frappe.db.set_value("Reconciliation Item", item.name, "approved_by", frappe.session.user)
    
    # Create expense entries
    create_expense_entries_for_items(doc, items_to_approve)
    
    # Recalculate totals
    total_approved_amount = frappe.db.sql("""
        SELECT COALESCE(SUM(amount), 0) as total
        FROM `tabReconciliation Item`
        WHERE parent = %s
        AND reconciliation_status = 'Approved'
    """, (doc.name,), as_dict=1)[0].total
    
    doc.db_set("total_reconciled_amount", total_approved_amount)
    
    variance = flt(doc.approved_amount) - flt(total_approved_amount)
    doc.db_set("variance_amount", variance)
    
    pending_items = frappe.db.count("Reconciliation Item", {
        "parent": doc.name,
        "reconciliation_status": "Pending"
    })
    
    remaining_to_reconcile = flt(doc.approved_amount) - flt(total_approved_amount)
    
    # Update status
    if pending_items == 0 and abs(remaining_to_reconcile) < 1.0:
        if abs(variance) >= 1.0:
            doc.db_set("reconciliation_status", "Reconciled - Variance Pending")
        else:
            doc.db_set("reconciliation_status", "Fully Reconciled")
        doc.db_set("reconciliation_completed_date", now())
        
        if abs(variance) >= 1.0:
            frappe.msgprint(_(
                "Reconciliation complete. Variance: {0}. Use 'Create Variance JE' button to settle."
            ).format(frappe.format_value(variance, {'fieldtype': 'Currency'})))
        else:
            frappe.msgprint(_("Reconciliation complete with no variance!"))
        
        send_reconciliation_completion_notification(doc)
        
    elif pending_items == 0 and remaining_to_reconcile >= 1.0:
        doc.db_set("reconciliation_status", "Partially Reconciled")
        frappe.msgprint(_("Need more receipts for {0}").format(
            frappe.format_value(remaining_to_reconcile, {'fieldtype': 'Currency'})
        ))
        send_more_receipts_needed_notification(doc, remaining_to_reconcile)
        
    else:
        approved_count = frappe.db.count("Reconciliation Item", {
            "parent": doc.name,
            "reconciliation_status": "Approved"
        })
        rejected_count = frappe.db.count("Reconciliation Item", {
            "parent": doc.name,
            "reconciliation_status": "Rejected"
        })
        
        if approved_count > 0 or rejected_count > 0:
            doc.db_set("reconciliation_status", "Partially Reconciled")
        else:
            doc.db_set("reconciliation_status", "Pending Review")
    
    return {
        "success": True,
        "approved_items": len(items_to_approve),
        "total_reconciled": total_approved_amount,
        "variance": variance,
        "status": doc.reconciliation_status
    }


@frappe.whitelist()
def reject_reconciliation_items(imprest_request, item_names, rejection_reason):
    """Finance rejects items"""
    doc = frappe.get_doc("Imprest Request", imprest_request)
    
    if not item_names:
        frappe.throw(_("Select at least one item"))
    
    if isinstance(item_names, str):
        item_names = json.loads(item_names)
    
    rejected_items_details = []
    for item_name in item_names:
        item = frappe.get_doc("Reconciliation Item", item_name)
        frappe.db.set_value("Reconciliation Item", item_name, "reconciliation_status", "Rejected")
        frappe.db.set_value("Reconciliation Item", item_name, "rejection_reason", rejection_reason)
        frappe.db.set_value("Reconciliation Item", item_name, "rejected_date", now())
        frappe.db.set_value("Reconciliation Item", item_name, "rejected_by", frappe.session.user)
        
        rejected_items_details.append({
            "category": item.expense_category,
            "amount": item.amount,
            "description": item.description
        })
    
    # Check status
    pending_items = frappe.db.count("Reconciliation Item", {
        "parent": doc.name,
        "reconciliation_status": "Pending"
    })
    
    total_reconciled = flt(doc.total_reconciled_amount or 0)
    remaining = flt(doc.approved_amount) - total_reconciled
    
    if pending_items == 0 and abs(remaining) < 1.0:
        variance = flt(doc.approved_amount) - total_reconciled
        if abs(variance) >= 1.0:
            doc.db_set("reconciliation_status", "Reconciled - Variance Pending")
        else:
            doc.db_set("reconciliation_status", "Fully Reconciled")
        doc.db_set("reconciliation_completed_date", now())
    elif pending_items == 0 and remaining >= 1.0:
        doc.db_set("reconciliation_status", "Partially Reconciled")
        send_more_receipts_needed_notification(doc, remaining)
    else:
        approved = frappe.db.count("Reconciliation Item", {
            "parent": doc.name,
            "reconciliation_status": "Approved"
        })
        rejected = frappe.db.count("Reconciliation Item", {
            "parent": doc.name,
            "reconciliation_status": "Rejected"
        })
        doc.db_set("reconciliation_status", "Partially Reconciled" if (approved > 0 or rejected > 0) else "Pending Review")
    
    send_rejection_notification(doc, rejected_items_details, rejection_reason)
    
    frappe.msgprint(_("{0} items rejected").format(len(item_names)))
    
    return {"success": True}


def create_expense_entries_for_items(doc, items_to_approve):
    """
    Create expense booking JE
    
    CORRECT ACCOUNTING FOR EXPENSE RECONCILIATION:
    When employee submits receipts and we approve them:
    Dr. Expense Account(s) (Expense increases)
    Cr. Employee Advance (ASSET DECREASES - employee owes us less / has settled)
    """
    employee_account = doc.get_employee_advance_account()
    
    category_totals = {}
    for item in items_to_approve:
        category = item.expense_category
        if category not in category_totals:
            category_totals[category] = 0
        category_totals[category] += flt(item.amount)
    
    je = frappe.new_doc("Journal Entry")
    je.voucher_type = "Journal Entry"
    je.posting_date = nowdate()
    je.company = doc.company
    je.user_remark = f"Expense booking for {doc.name} ({len(items_to_approve)} items)"
    je.imprest_request = doc.name
    
    total_amount = 0
    for category, amount in category_totals.items():
        expense_account = get_expense_account_for_category(category, doc.company)
        
        # Debit Expense Accounts (Expense increases)
        je.append("accounts", {
            "account": expense_account,
            "debit_in_account_currency": flt(amount, 2),
            "credit_in_account_currency": 0,
            "cost_center": doc.cost_center if doc.cost_center else None
        })
        total_amount += flt(amount, 2)
    
    # Credit Employee Advance (ASSET DECREASES - employee has settled this amount)
    je.append("accounts", {
        "account": employee_account,
        "debit_in_account_currency": 0,
        "credit_in_account_currency": total_amount,
        "party_type": "Employee",
        "party": doc.employee
    })
    
    je.flags.ignore_permissions = True
    je.insert()
    je.submit()
    
    existing_je = doc.expense_booking_journal_entry
    if existing_je:
        doc.db_set("expense_booking_journal_entry", f"{existing_je}, {je.name}")
    else:
        doc.db_set("expense_booking_journal_entry", je.name)


@frappe.whitelist()
def approve_reconciliation(imprest_request):
    """Legacy: Approve all items"""
    doc = frappe.get_doc("Imprest Request", imprest_request)
    all_item_names = [item.name for item in doc.reconciliation_items]
    return approve_reconciliation_items(imprest_request, all_item_names)


def get_expense_account_for_category(category, company):
    """Get validated expense account"""
    account = frappe.db.get_value("Imprest Expense Category", category, "expense_account")
    
    if not account:
        frappe.throw(_("No expense account for category {0}").format(category))
    
    account_details = frappe.db.get_value("Account", account, 
        ["name", "is_group", "disabled", "company"], 
        as_dict=1)
    
    if not account_details:
        frappe.throw(_("Account {0} not found").format(account))
    
    if account_details.is_group:
        frappe.throw(_("Account {0} is a group account").format(account))
    
    if account_details.disabled:
        frappe.throw(_("Account {0} is disabled").format(account))
    
    if account_details.company != company:
        frappe.throw(_("Account company mismatch"))
    
    return account


# ============================================================================
# NOTIFICATION FUNCTIONS
# ============================================================================

def notify_finance_team_for_reconciliation(doc, total_submitted=None, items_count=None):
    """Notify finance team"""
    settings = frappe.get_doc("Imprest Management Settings")
    
    if not settings.finance_manager_email:
        return
    
    if total_submitted is None:
        pending = [i for i in doc.reconciliation_items if i.reconciliation_status == "Pending"]
        total_submitted = sum(flt(i.amount) for i in pending)
        items_count = len(pending)
    elif items_count is None:
        items_count = len([i for i in doc.reconciliation_items if i.reconciliation_status == "Pending"])
    
    total_reconciled = flt(doc.total_reconciled_amount or 0)
    remaining = flt(doc.approved_amount) - total_reconciled
    
    message = f"""
    <h2>New Receipts Submitted</h2>
    <p>Employee: {doc.employee_name}</p>
    <p>New items: {items_count} ({frappe.format_value(total_submitted, {'fieldtype': 'Currency'})})</p>
    <p>Previously approved: {frappe.format_value(total_reconciled, {'fieldtype': 'Currency'})}</p>
    <p>Remaining: {frappe.format_value(remaining, {'fieldtype': 'Currency'})}</p>
    <p><a href="{frappe.utils.get_url()}/app/imprest-request/{doc.name}">Review</a></p>
    """
    
    frappe.sendmail(
        recipients=[settings.finance_manager_email],
        subject=f"New Receipts - {doc.name}",
        message=message
    )


def send_rejection_notification(doc, items, reason):
    """Notify employee of rejections"""
    email = frappe.db.get_value("Employee", doc.employee, "user_id")
    if not email:
        return
    
    items_html = "".join([
        f"<tr><td>{i['category']}</td><td>{i['description']}</td><td>{frappe.format_value(i['amount'], {'fieldtype': 'Currency'})}</td></tr>"
        for i in items
    ])
    
    message = f"""
    <h2>Items Rejected</h2>
    <p>Reason: {reason}</p>
    <table><thead><tr><th>Category</th><th>Description</th><th>Amount</th></tr></thead>
    <tbody>{items_html}</tbody></table>
    <p><a href="{frappe.utils.get_url()}/app/imprest-request/{doc.name}">Resubmit</a></p>
    """
    
    frappe.sendmail(
        recipients=[email],
        subject=f"Items Rejected - {doc.name}",
        message=message
    )


def send_more_receipts_needed_notification(doc, remaining):
    """Notify more receipts needed"""
    email = frappe.db.get_value("Employee", doc.employee, "user_id")
    if not email:
        return
    
    message = f"""
    <h2>More Receipts Needed</h2>
    <p>Approved: {frappe.format_value(doc.approved_amount, {'fieldtype': 'Currency'})}</p>
    <p>Reconciled: {frappe.format_value(doc.total_reconciled_amount, {'fieldtype': 'Currency'})}</p>
    <p>Still need: {frappe.format_value(remaining, {'fieldtype': 'Currency'})}</p>
    <p><a href="{frappe.utils.get_url()}/app/imprest-request/{doc.name}">Submit More</a></p>
    """
    
    frappe.sendmail(
        recipients=[email],
        subject=f"More Receipts Needed - {doc.name}",
        message=message
    )


def send_reconciliation_completion_notification(doc):
    """Notify reconciliation complete"""
    email = frappe.db.get_value("Employee", doc.employee, "user_id")
    if not email:
        return
    
    variance_msg = ""
    if flt(doc.variance_amount) > 0:
        variance_msg = f"<p style='color: green;'>Refund due: {frappe.format_value(doc.variance_amount, {'fieldtype': 'Currency'})}</p>"
    elif flt(doc.variance_amount) < 0:
        variance_msg = f"<p style='color: orange;'>Additional payment due: {frappe.format_value(abs(doc.variance_amount), {'fieldtype': 'Currency'})}</p>"
    else:
        variance_msg = "<p style='color: green;'>Perfect match - no variance!</p>"
    
    message = f"""
    <h2>✓ Reconciliation Complete</h2>
    <p>Approved: {frappe.format_value(doc.approved_amount, {'fieldtype': 'Currency'})}</p>
    <p>Spent: {frappe.format_value(doc.total_reconciled_amount, {'fieldtype': 'Currency'})}</p>
    {variance_msg}
    <p>Finance will create a Journal Entry to settle any variance.</p>
    """
    
    frappe.sendmail(
        recipients=[email],
        subject=f"Reconciliation Complete - {doc.name}",
        message=message
    )


# ============================================================================
# DASHBOARD & REPORTS
# ============================================================================

@frappe.whitelist()
def get_imprest_dashboard_data():
    """Dashboard data"""
    
    pending_approvals = frappe.db.count("Imprest Request", {
        "workflow_state": "Pending Approval",
        "docstatus": 0
    })
    
    pending_reconciliations = frappe.db.count("Imprest Request", {
        "reconciliation_status": ["in", ["Pending Review", "Partially Reconciled", "Reconciled - Variance Pending"]],
        "docstatus": 1
    })
    
    return {
        "summary": {
            "pending_approvals": pending_approvals,
            "pending_reconciliations": pending_reconciliations
        }
    }


@frappe.whitelist()
def get_event_imprest_summary(event_name):
    """Event summary"""
    
    requests = frappe.db.sql("""
        SELECT name, employee_name, approved_amount, total_reconciled_amount
        FROM `tabImprest Request`
        WHERE event = %s
        ORDER BY posting_date DESC
    """, (event_name,), as_dict=1)
    
    total_approved = sum(flt(r.approved_amount) for r in requests)
    total_spent = sum(flt(r.total_reconciled_amount) for r in requests if r.total_reconciled_amount)
    
    return {
        "requests": requests,
        "total_approved": total_approved,
        "total_spent": total_spent,
        "balance": total_approved - total_spent
    }