# Deployment Checklist for Imprest Management System

## Pre-Installation Checklist

- [ ] Frappe version 14.0 or higher
- [ ] ERPNext installed (for accounting features)
- [ ] Event Management module installed (for event integration)
- [ ] Chart of Accounts configured
- [ ] At least one company created
- [ ] Employee master data available
- [ ] Email settings configured

## Installation Steps

### Step 1: File Deployment
Copy these files to your Frappe app structure:

```
your_app/
├── accounts/
│   ├── doctype/
│   │   ├── imprest_request/
│   │   │   ├── __init__.py
│   │   │   ├── imprest_request.json
│   │   │   ├── imprest_request.py
│   │   │   ├── imprest_request.js
│   │   │   └── test_imprest_request.py
│   │   │
│   │   ├── imprest_expense_item/
│   │   │   ├── __init__.py
│   │   │   └── imprest_expense_item.json
│   │   │
│   │   ├── reconciliation_item/
│   │   │   ├── __init__.py
│   │   │   └── reconciliation_item.json
│   │   │
│   │   ├── imprest_expense_category/
│   │   │   ├── __init__.py
│   │   │   ├── imprest_expense_category.json
│   │   │   └── imprest_expense_category.py
│   │   │
│   │   └── imprest_management_settings/
│   │       ├── __init__.py
│   │       ├── imprest_management_settings.json
│   │       └── imprest_management_settings.py
│   │
│   └── report/
│       ├── imprest_summary_report/
│       │   ├── __init__.py
│       │   ├── imprest_summary_report.json
│       │   ├── imprest_summary_report.py
│       │   └── imprest_summary_report.js
│       │
│       ├── event_wise_imprest_report/
│       │   ├── __init__.py
│       │   ├── event_wise_imprest_report.json
│       │   └── event_wise_imprest_report.py
│       │
│       └── category_wise_expense_report/
│           ├── __init__.py
│           ├── category_wise_expense_report.json
│           └── category_wise_expense_report.py
```

### Step 2: Run Migration

```bash
cd frappe-bench

# Run database migration
bench --site [your-site] migrate

# Clear cache
bench --site [your-site] clear-cache

# Rebuild
bench build
```

### Step 3: Setup Master Data

```bash
# Open Frappe console
bench --site [your-site] console

# Run setup script
from your_app.setup_sample_data import execute
execute()
```

### Step 4: Configure Settings

1. Navigate to: **Imprest Management Settings**

2. Set these values:
   ```
   Employee Advance Parent Account: [Auto-created "Employee Advances"]
   Default Source Account: [Your main bank account]
   Default Company: [Your company]
   Finance Manager Email: [Email address]
   ✓ Send Approval Notifications
   ✓ Send Reconciliation Notifications
   ✓ Require Manager Approval
   Auto Approve Threshold: 5000 (or your preference)
   ```

### Step 5: Verify Installation

Run these checks:

```python
# In Frappe console
import frappe

# Check DocTypes
print("Checking DocTypes...")
doctypes = [
    "Imprest Request",
    "Imprest Expense Item",
    "Reconciliation Item",
    "Imprest Expense Category",
    "Imprest Management Settings"
]
for dt in doctypes:
    exists = frappe.db.exists("DocType", dt)
    print(f"  {dt}: {'✓' if exists else '✗'}")

# Check Reports
print("
Checking Reports...")
reports = [
    "Imprest Summary Report",
    "Event-wise Imprest Report",
    "Category-wise Expense Analysis"
]
for rpt in reports:
    exists = frappe.db.exists("Report", rpt)
    print(f"  {rpt}: {'✓' if exists else '✗'}")

# Check Expense Categories
print("
Checking Expense Categories...")
categories = frappe.get_all("Imprest Expense Category", pluck="name")
print(f"  Found {len(categories)} categories")
for cat in categories:
    print(f"    - {cat}")
```

### Step 6: User Training

Create these user guides:
- [ ] Employee guide for creating requests
- [ ] Finance manager guide for approvals
- [ ] Reconciliation process guide
- [ ] Report usage guide

## Post-Installation Configuration

### 1. Account Structure Verification

Ensure these accounts exist:

```
Chart of Accounts
├── Assets
│   └── Current Assets
│       └── Employee Advances (Group) ← Parent for all employee advances
│           └── [Employee Name] - Advance ← Auto-created per employee
│
└── Expenses
    └── Operating Expenses
        ├── Transport Expense
        ├── Accommodation Expense
        ├── Food & Beverage Expense
        ├── Training Expense
        ├── Entertainment Expense
        ├── Venue Rental
        ├── Telephone Expense
        └── Miscellaneous Expense
```

### 2. Create Missing Accounts

If any expense accounts are missing, create them:

```python
def create_expense_account(account_name, company):
    """Helper to create expense account"""
    import frappe
    
    company_abbr = frappe.db.get_value("Company", company, "abbr")
    full_name = f"{account_name} - {company_abbr}"
    
    if not frappe.db.exists("Account", full_name):
        # Get parent account
        parent = frappe.db.get_value("Account", {
            "account_name": "Operating Expenses",
            "company": company,
            "is_group": 1
        })
        
        doc = frappe.new_doc("Account")
        doc.account_name = account_name
        doc.parent_account = parent
        doc.company = company
        doc.is_group = 0
        doc.account_type = "Expense Account"
        doc.insert()
        
        print(f"Created: {full_name}")
    else:
        print(f"Exists: {full_name}")

# Usage
company = frappe.defaults.get_global_default("company")
accounts = [
    "Transport Expense",
    "Accommodation Expense", 
    "Food & Beverage Expense",
    "Training Expense",
    "Entertainment Expense",
    "Venue Rental",
    "Telephone Expense",
    "Miscellaneous Expense"
]

for acc in accounts:
    create_expense_account(acc, company)
```

### 3. Setup Permissions

Verify role permissions:

```python
def setup_permissions():
    """Setup role permissions for imprest doctypes"""
    import frappe
    
    # Imprest Request permissions
    frappe.db.sql("""
        DELETE FROM `tabCustom DocPerm` 
        WHERE parent = 'Imprest Request'
    """)
    
    # Employee - Can create and view own
    frappe.get_doc({
        "doctype": "Custom DocPerm",
        "parent": "Imprest Request",
        "role": "Employee",
        "read": 1,
        "write": 1,
        "create": 1,
        "if_owner": 1
    }).insert()
    
    # Accounts User - Full access
    frappe.get_doc({
        "doctype": "Custom DocPerm",
        "parent": "Imprest Request",
        "role": "Accounts User",
        "read": 1,
        "write": 1,
        "create": 1,
        "submit": 1,
        "cancel": 1
    }).insert()
    
    # Accounts Manager - Full access + delete
    frappe.get_doc({
        "doctype": "Custom DocPerm",
        "parent": "Imprest Request",
        "role": "Accounts Manager",
        "read": 1,
        "write": 1,
        "create": 1,
        "submit": 1,
        "cancel": 1,
        "delete": 1
    }).insert()
    
    frappe.db.commit()
    print("Permissions setup complete")

setup_permissions()
```

### 4. Email Template Setup

Create email templates (optional - system has defaults):

1. Go to: **Email Template** → **New**
2. Create: "Imprest Approval Notification"
3. Create: "Imprest Rejection Notification"
4. Create: "Reconciliation Approval Notification"

### 5. Workflow Setup (Optional)

For multi-level approval, create workflow:

1. Go to: **Workflow** → **New**
2. Document Type: Imprest Request
3. States:
   - Draft
   - Pending Manager Approval
   - Pending Finance Approval
   - Approved
   - Rejected
4. Transitions:
   - Draft → Pending Manager Approval (Employee)
   - Pending Manager → Pending Finance (Manager)
   - Pending Finance → Approved (Finance Manager)
   - Any → Rejected (Manager/Finance)

## Testing Checklist

### Basic Functionality Tests

- [ ] Create imprest request as employee
- [ ] Save draft and edit
- [ ] Submit for approval
- [ ] Receive email notification
- [ ] Approve as finance manager
- [ ] Verify disbursement entry created
- [ ] Check employee advance account balance
- [ ] Add reconciliation items
- [ ] Upload receipt files
- [ ] Submit reconciliation
- [ ] Approve reconciliation
- [ ] Verify expense entries created
- [ ] Verify variance handling
- [ ] Check final account balances

### Integration Tests

- [ ] Link request to event
- [ ] View event imprest summary
- [ ] Verify event totals
- [ ] Check category breakdown per event
- [ ] Run all reports with filters
- [ ] Export reports to Excel
- [ ] Test dashboard data accuracy

### Edge Cases

- [ ] Reject and resubmit request
- [ ] Reject and resubmit reconciliation
- [ ] Over-spend scenario (negative variance)
- [ ] Under-spend scenario (positive variance)
- [ ] Zero variance reconciliation
- [ ] Multiple requests for same event
- [ ] Request without event
- [ ] Cancel approved request
- [ ] Amend submitted request

## Performance Optimization

After installation, run these optimizations:

```sql
-- Add indexes for better performance
ALTER TABLE `tabImprest Request` 
ADD INDEX idx_employee (employee);

ALTER TABLE `tabImprest Request` 
ADD INDEX idx_event (event);

ALTER TABLE `tabImprest Request` 
ADD INDEX idx_posting_date (posting_date);

ALTER TABLE `tabImprest Request` 
ADD INDEX idx_workflow_state (workflow_state);

ALTER TABLE `tabReconciliation Item` 
ADD INDEX idx_expense_category (expense_category);
```

## Backup & Rollback

Before going live:

```bash
# Backup database
bench --site [your-site] backup

# Backup files
cd frappe-bench/sites/[your-site]
tar -czf site-backup-$(date +%Y%m%d).tar.gz .

# To rollback if needed
bench --site [your-site] restore [backup-file]
```

## Go-Live Checklist

- [ ] All tests passed
- [ ] Sample data created and verified
- [ ] User training completed
- [ ] Documentation distributed
- [ ] Backup taken
- [ ] Email notifications tested
- [ ] Reports verified
- [ ] Accounting entries reviewed
- [ ] Finance manager trained
- [ ] Employees trained
- [ ] Help desk briefed

## Monitoring & Maintenance

### Daily Checks
- [ ] Review pending approvals
- [ ] Check email queue for failures
- [ ] Monitor reconciliation submissions

### Weekly Checks
- [ ] Run imprest summary report
- [ ] Review outstanding advances
- [ ] Check for stale draft requests

### Monthly Checks
- [ ] Reconcile employee advance accounts
- [ ] Review expense categories usage
- [ ] Analyze spending patterns
- [ ] Archive completed requests (older than 6 months)

### Quarterly Checks
- [ ] Review and update expense categories
- [ ] Audit approval thresholds
- [ ] User feedback review
- [ ] System performance review

## Troubleshooting Guide

### Issue: Disbursement entry not created

**Symptoms**: Approved request but no journal entry

**Solutions**:
1. Check error log
2. Verify source account exists
3. Check user permissions for Journal Entry
4. Verify employee advance account created
5. Check company default currency

**Fix**:
```python
# Manually trigger disbursement
doc = frappe.get_doc("Imprest Request", "IMP-2026-00001")
doc.create_disbursement_entry()
```

### Issue: Email notifications not working

**Symptoms**: No emails being sent

**Solutions**:
1. Check Email Account setup
2. Verify SMTP settings
3. Check Email Queue for errors
4. Verify recipient email addresses
5. Check settings.send_approval_notifications

**Fix**:
```python
# Test email
frappe.sendmail(
    recipients=["test@example.com"],
    subject="Test",
    message="Test email from Imprest System"
)
```

### Issue: Reconciliation variance incorrect

**Symptoms**: Wrong variance calculation

**Solutions**:
1. Refresh document (Ctrl+R)
2. Check reconciliation_items total
3. Verify approved_amount is correct
4. Check for rounding issues

**Fix**:
```python
# Recalculate manually
doc = frappe.get_doc("Imprest Request", "IMP-2026-00001")
total = sum(item.amount for item in doc.reconciliation_items)
doc.db_set("total_reconciled_amount", total)
doc.db_set("variance_amount", doc.approved_amount - total)
```

## Support Resources

- **Documentation**: README.md, IMPLEMENTATION_GUIDE.md
- **Sample Code**: setup_sample_data.py
- **Test Cases**: test_imprest_request.py
- **Community**: Frappe Forum, ERPNext Forum
- **Professional Support**: support@yourcompany.com

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Jan 2026 | Initial release |
| 1.0.1 | TBD | Bug fixes and optimizations |

---

**Note**: Always test in a staging environment before deploying to production!
