import frappe
from frappe.model.document import Document
from frappe import _


class ImprestManagementSettings(Document):
    def validate(self):
        """Validation before saving"""
        # Validate email address if provided
        if self.finance_manager_email:
            from frappe.utils import validate_email_address
            validate_email_address(self.finance_manager_email, throw=True)
        
        # Ensure parent account exists and is of correct type
        if self.employee_advance_parent_account:
            account_type = frappe.db.get_value(
                "Account", 
                self.employee_advance_parent_account, 
                ["account_type", "is_group"]
            )
            
            if account_type and account_type[1] != 1:
                frappe.msgprint(_("Employee Advance Parent Account should be a group account"))
        
        # Validate default source account if provided
        if self.default_source_account:
            account_details = frappe.db.get_value(
                "Account",
                self.default_source_account,
                ["account_type", "is_group", "disabled"],
                as_dict=1
            )
            
            if account_details:
                if account_details.is_group:
                    frappe.throw(_("Default Source Account cannot be a group account. Please select a ledger account."))
                
                if account_details.disabled:
                    frappe.throw(_("Default Source Account is disabled. Please select an active account."))
                
                if account_details.account_type not in ["Bank", "Cash"]:
                    frappe.msgprint(
                        _("Default Source Account should typically be a Bank or Cash account."),
                        alert=True,
                        indicator="orange"
                    )