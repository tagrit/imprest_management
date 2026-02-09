# Imprest Management System - Implementation Guide

## Overview
This is a complete imprest (cash advance) management system for Frappe/ERPNext that integrates seamlessly with your Event Management module. It handles the full lifecycle of employee cash advances from request to reconciliation with automated accounting entries.

## Features

### 1. **Imprest Request Management**
- Employees can request cash advances for events or general purposes
- Dynamic expense categories with sub-categories
- Link to Event Registration for event-specific tracking
- Multi-line expense item entry with quantity and rates

### 2. **Approval Workflow**
- Finance manager review and approval
- Ability to adjust approved amount from requested amount
- Rejection with comments and employee resubmission
- Email notifications at each stage

### 3. **Automated Accounting**
- Disbursement: Moves funds from bank/cash to employee advance account
- Reconciliation: Books expenses to appropriate GL accounts based on category
- Variance handling: Automatic refund or additional payment processing
- All entries create proper Journal Entries with full audit trail

### 4. **Reconciliation Process**
- Employees upload receipts for actual expenses
- Finance manager reviews and approves/rejects
- System calculates variance automatically
- Categorizes expenses and posts to correct accounts

### 5. **Event Integration**
- Track all imprest requests per event
- View event-wise expense summary
- Category breakdown for each event
- Total approved vs spent analysis

### 6. **Reporting & Analytics**
- Imprest Summary Report (with charts)
- Event-wise Imprest Analysis
- Category-wise Expense Analysis
- Dashboard with KPIs

## Installation Steps

### Step 1: Create DocTypes

Create the following DocTypes in your app:

#### A. Imprest Request (Main DocType)
```bash
bench new-doctype "Imprest Request"
```
- Copy the JSON from `imprest_request.json`
- Copy the Python controller from `imprest_request.py`

#### B. Imprest Expense Item (Child Table)
```bash
bench new-doctype "Imprest Expense Item"
```
- Copy the JSON from `imprest_expense_item.json`

#### C. Reconciliation Item (Child Table)
```bash
bench new-doctype "Reconciliation Item"
```
- Copy the JSON from `reconciliation_item.json`

#### D. Imprest Expense Category
```bash
bench new-doctype "Imprest Expense Category"
```
- Copy the JSON from `imprest_expense_category.json`
- Copy the Python controller from `imprest_expense_category.py`

#### E. Imprest Management Settings (Single DocType)
```bash
bench new-doctype "Imprest Management Settings"
```
- Copy the JSON from `imprest_management_settings.json`
- Copy the Python controller from `imprest_management_settings.py`

### Step 2: Add Custom Fields to Journal Entry

Add a custom field to link Journal Entries back to Imprest Requests:

```python
# In hooks.py or a patch
custom_field = {
    'Journal Entry': [
        {
            'fieldname': 'imprest_request',
            'label': 'Imprest Request',
            'fieldtype': 'Link',
            'options': 'Imprest Request',
            'insert_after': 'user_remark'
        }
    ]
}
```

### Step 3: Create Client Scripts

Add the client script for enhanced UX:
- File: `imprest_request_client.js`
- Location: `[your_app]/[module]/doctype/imprest_request/imprest_request.js`

### Step 4: Create Reports

#### A. Imprest Summary Report
```bash
bench new-report "Imprest Summary Report"
```
- Type: Script Report
- Module: Accounts
- Copy files:
  - `imprest_summary_report.py`
  - `imprest_summary_report.js`

#### B. Event-wise Imprest Report
```bash
bench new-report "Event-wise Imprest Report"
```
- Copy `event_wise_imprest_report.py`

#### C. Category-wise Expense Analysis
```bash
bench new-report "Category-wise Expense Analysis"
```
- Copy `category_wise_expense_report.py`

### Step 5: Initial Setup

1. **Navigate to Imprest Management Settings**
   - Set Employee Advance Parent Account (create if doesn't exist)
   - Set Default Source Account (your main bank account)
   - Set Finance Manager Email
   - Set Default Company and Cost Center

2. **Create Expense Categories**
   Create categories like:
   - Transport (mapped to Transport Expense account)
   - Accommodation (mapped to Accommodation Expense account)
   - Meals & Refreshments (mapped to Food & Beverage Expense account)
   - Training Materials (mapped to Training Expense account)
   - Host Stay (mapped to Hospitality Expense account)

3. **Set Up Accounts**
   Ensure you have these accounts in your Chart of Accounts:
   ```
   Assets
   └── Current Assets
       └── Employee Advances (Group)
           └── [Employee Name] - Advance (Auto-created per employee)
   
   Expenses
   └── Operating Expenses
       ├── Transport Expense
       ├── Accommodation Expense
       ├── Food & Beverage Expense
       ├── Training Expense
       └── Hospitality Expense
   ```

## Usage Workflow

### For Employees:

1. **Create Imprest Request**
   - Go to Imprest Request > New
   - Select yourself as Employee
   - Optionally link to an Event
   - Add expense items with categories and amounts
   - Save and Submit for Approval

2. **After Approval**
   - Funds are automatically disbursed to your advance account
   - Make the purchases/payments
   - Upload receipts in Reconciliation section
   - Click "Submit Reconciliation"

3. **After Reconciliation Approval**
   - System automatically books expenses
   - Any variance (over/under spend) is handled
   - Your advance account is cleared

### For Finance Managers:

1. **Approve Requests**
   - Review pending imprest requests
   - Adjust approved amount if needed
   - Approve or Reject with comments
   - System creates disbursement entry automatically

2. **Review Reconciliations**
   - Check uploaded receipts
   - Verify amounts and categories
   - Approve or Reject
   - System creates final accounting entries

### For Event Managers:

1. **Track Event Expenses**
   - Open any Event Registration
   - Click "View Imprest Summary" (custom button)
   - See all imprest requests linked to event
   - View category breakdown
   - Monitor budget vs actual

## Accounting Flow

### 1. Disbursement (On Approval)
```
DR: Employee Advance Account (Asset)     XXX
    CR: Bank Account                         XXX
```

### 2. Expense Booking (On Reconciliation)
```
DR: Transport Expense                    XXX
DR: Meals Expense                        XXX
DR: Accommodation Expense                XXX
    CR: Employee Advance Account             XXX
```

### 3. Variance Handling

**If employee spent less (refund):**
```
DR: Bank Account                         XXX
    CR: Employee Advance Account             XXX
```

**If employee spent more (additional payment):**
```
DR: Employee Advance Account             XXX
    CR: Bank Account                         XXX
```

## Key Features Explained

### Dynamic Categories & Sub-Categories
- Main categories (e.g., "Meals") map to GL accounts
- Sub-categories (e.g., "Breakfast", "Lunch", "Dinner") are descriptive only
- Allows detailed tracking without cluttering Chart of Accounts

### Event Integration
- Link imprest to events for better tracking
- Auto-populate purpose from event details
- View all event expenses in one place
- Category breakdown per event

### Workflow States
1. **Draft**: Initial creation
2. **Pending Approval**: Submitted by employee
3. **Approved**: Finance approved, funds disbursed
4. **Rejected**: Needs revision

### Reconciliation States
1. **Null**: Not yet submitted
2. **Pending Review**: Employee submitted receipts
3. **Completed**: Finance approved, expenses booked
4. **Rejected**: Needs revision

### Email Notifications
- Approval notification to employee
- Reconciliation submission to finance
- Rejection notifications with reasons

## Reports Explained

### 1. Imprest Summary Report
- Filters: Date range, employee, event, status
- Shows: All requests with amounts, status, variance
- Chart: Approved vs Reconciled comparison
- Summary: Total requested, approved, reconciled, variance

### 2. Event-wise Imprest Report
- Groups all imprest by event
- Shows total approved and spent per event
- Completion percentage
- Helps track event budgets

### 3. Category-wise Expense Analysis
- Breaks down expenses by category
- Shows transaction counts and averages
- Percentage distribution
- Donut chart visualization

## Customization Points

### 1. Approval Hierarchy
You can add multi-level approvals by:
- Creating custom workflow
- Adding workflow states
- Setting role permissions

### 2. Auto-Approval Threshold
In Settings, set an amount below which requests are auto-approved.

### 3. Custom Categories
Add as many categories as needed:
- Transport > Taxi, Uber, Bus
- Meals > Breakfast, Lunch, Dinner, Snacks
- Accommodation > Hotel, Airbnb
- Host Stay > Lunch, Breakfast, Gifts

### 4. Integration with Event Module
The system already integrates with your Event Registration. You can extend this by:
- Adding imprest budget to Event Registration
- Showing warnings when budget exceeded
- Auto-creating imprest requests from events

### 5. Mobile Access
All forms are mobile-responsive. Employees can:
- Submit requests from phone
- Upload receipt photos directly
- Check approval status

## Permissions

### Employee Role
- Create imprest requests
- View own requests
- Submit reconciliations
- Upload receipts

### Accounts Manager Role
- View all requests
- Approve/reject requests
- Adjust amounts
- Review reconciliations
- Access all reports

### Accounts User Role
- View all requests
- Submit requests on behalf of employees
- Access reports

## Best Practices

1. **Always link to events when applicable** - Helps with event cost tracking
2. **Use consistent sub-categories** - Makes reporting more meaningful
3. **Upload clear receipt photos** - Speeds up approval
4. **Submit reconciliation within 7 days** - Keeps accounts current
5. **Review pending requests weekly** - Avoid backlog
6. **Run monthly expense reports** - Identify spending patterns

## Troubleshooting

### Disbursement Entry Not Created
- Check if approved amount is set
- Verify source account is configured
- Check employee advance parent account exists

### Cannot Submit Reconciliation
- Ensure receipts are uploaded
- Check amounts are entered
- Verify categories are selected

### Accounting Entry Errors
- Verify expense accounts exist for all categories
- Check company currency settings
- Ensure cost center is valid

### Email Notifications Not Sending
- Check email settings in ERPNext
- Verify finance manager email in settings
- Check email queue for errors

## Future Enhancements

Potential additions:
1. Mobile app for quick expense submission
2. OCR for automatic receipt scanning
3. Integration with corporate cards
4. Budget enforcement at category level
5. Automated reminder emails for pending reconciliations
6. Bulk approval interface
7. Expense policy compliance checks

## Support & Maintenance

- Regular backups of Imprest Request doctype
- Monthly cleanup of old draft requests
- Quarterly review of expense categories
- Annual audit of employee advance accounts

## File Structure
```
your_app/
├── your_module/
│   ├── doctype/
│   │   ├── imprest_request/
│   │   │   ├── imprest_request.json
│   │   │   ├── imprest_request.py
│   │   │   └── imprest_request.js
│   │   ├── imprest_expense_item/
│   │   ├── reconciliation_item/
│   │   ├── imprest_expense_category/
│   │   └── imprest_management_settings/
│   └── report/
│       ├── imprest_summary_report/
│       ├── event_wise_imprest_report/
│       └── category_wise_expense_report/
```

## Conclusion

This imprest management system provides complete tracking and accounting for employee cash advances with seamless integration to your event management module. The automated accounting ensures accuracy while the approval workflow maintains control.

Happy implementing! 🚀
