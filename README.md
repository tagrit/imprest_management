# 💰 Imprest Management System for Frappe/ERPNext

A comprehensive cash advance management system that seamlessly integrates with your Event Management module. Track employee imprest requests from submission through reconciliation with automated accounting entries.

## ✨ Key Features

### 🎯 Core Functionality
- **Smart Request Management**: Create imprest requests with dynamic categories and sub-categories
- **Event Integration**: Link requests to events for comprehensive cost tracking
- **Approval Workflow**: Multi-stage approval with amount adjustments
- **Automated Accounting**: Automatic journal entries for disbursement, expenses, and variance handling
- **Receipt Management**: Upload and track receipts against actual expenses
- **Real-time Reconciliation**: Calculate variance and handle refunds/additional payments automatically

### 📊 Analytics & Reporting
- **Imprest Summary Report**: Complete overview with charts and KPIs
- **Event-wise Analysis**: Track all expenses per event
- **Category-wise Breakdown**: Understand spending patterns
- **Dashboard**: Real-time metrics and pending items

### 🔔 Notifications
- Automatic email notifications at each workflow stage
- Customizable notification settings
- Finance team alerts for pending approvals

## 🏗️ System Architecture

### Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    IMPREST REQUEST LIFECYCLE                     │
└─────────────────────────────────────────────────────────────────┘

1️⃣  EMPLOYEE CREATES REQUEST
    ├── Select event (optional)
    ├── Add expense items
    │   ├── Category (Transport, Meals, etc.)
    │   ├── Sub-category (Taxi, Lunch, etc.)
    │   └── Amount
    └── Submit for approval
              │
              ▼
2️⃣  FINANCE MANAGER REVIEWS
    ├── Approve (can adjust amount)
    │   └── System creates disbursement entry:
    │       DR: Employee Advance Account
    │       CR: Bank Account
    │
    └── Reject (with comments)
        └── Employee can revise & resubmit
              │
              ▼
3️⃣  EMPLOYEE MAKES PURCHASES
    ├── Spend the money
    ├── Collect receipts
    └── Upload receipts in system
        └── Categorize each expense
              │
              ▼
4️⃣  EMPLOYEE SUBMITS RECONCILIATION
    ├── System calculates variance
    │   └── Variance = Approved - Spent
    └── Notify finance team
              │
              ▼
5️⃣  FINANCE MANAGER REVIEWS RECONCILIATION
    ├── Approve
    │   ├── System creates expense entries:
    │   │   DR: Expense Accounts (by category)
    │   │   CR: Employee Advance Account
    │   │
    │   └── System handles variance:
    │       ├── If positive (refund to company):
    │       │   DR: Bank Account
    │       │   CR: Employee Advance Account
    │       │
    │       └── If negative (pay employee):
    │           DR: Employee Advance Account
    │           CR: Bank Account
    │
    └── Reject
        └── Employee corrects & resubmits
              │
              ▼
6️⃣  COMPLETE ✓
    └── All accounts balanced
```

## 📦 Components

### DocTypes

1. **Imprest Request** (Main)
   - Employee details
   - Event linkage
   - Expense items
   - Approval tracking
   - Reconciliation details
   - Accounting references

2. **Imprest Expense Item** (Child Table)
   - Category
   - Sub-category
   - Description
   - Quantity & Rate
   - Amount

3. **Reconciliation Item** (Child Table)
   - Category
   - Sub-category
   - Amount
   - Receipt attachment
   - Vendor details

4. **Imprest Expense Category**
   - Category name
   - GL account mapping
   - Company
   - Active status

5. **Imprest Management Settings** (Single)
   - Account configuration
   - Email settings
   - Approval thresholds
   - Default values

### Reports

1. **Imprest Summary Report**
   - Filter by date, employee, event, status
   - Bar chart: Approved vs Reconciled
   - Summary cards with KPIs

2. **Event-wise Imprest Report**
   - Groups by event
   - Shows budget vs actual
   - Completion percentages

3. **Category-wise Expense Analysis**
   - Donut chart of expense distribution
   - Transaction counts
   - Average amounts

## 🚀 Quick Start

### Installation

```bash
# 1. Create the module structure
cd frappe-bench/apps/your_app
bench new-app imprest_management

# 2. Install the app
bench --site your-site install-app imprest_management

# 3. Create DocTypes
# Copy all .json and .py files to appropriate locations

# 4. Run migrations
bench --site your-site migrate

# 5. Setup sample data
bench --site your-site console
>>> from imprest_management.setup_sample_data import execute
>>> execute()
```

### Initial Configuration

1. **Navigate to**: Imprest Management Settings

2. **Configure Accounts**:
   ```
   Employee Advance Parent Account: Employee Advances - [Company]
   Default Source Account: [Your Bank Account]
   Default Company: [Your Company]
   ```

3. **Setup Notifications**:
   ```
   Finance Manager Email: finance@yourcompany.com
   ✓ Send Approval Notifications
   ✓ Send Reconciliation Notifications
   ```

4. **Create Expense Categories**:
   - Go to: Imprest Expense Category
   - Create categories with GL account mappings:
     - Transport → Transport Expense
     - Meals & Refreshments → Food & Beverage Expense
     - Accommodation → Lodging Expense
     - etc.

## 📖 Usage Guide

### For Employees

#### Creating an Imprest Request

1. Go to **Imprest Request** → **New**
2. Fill in details:
   - Employee: [Auto-filled]
   - Event: [Optional - select from Event Registration]
   - Purpose: Brief description
   - Source Account: Bank to disburse from
3. Add expense items:
   - Category: Transport
   - Sub-category: Taxi
   - Description: Airport transfers
   - Quantity: 2
   - Rate: 2500
4. **Save** → **Submit for Approval**

#### Submitting Reconciliation

1. Open your approved imprest request
2. Scroll to **Reconciliation** section
3. Add reconciliation items:
   - Select category
   - Enter actual amount
   - Attach receipt (photo/PDF)
   - Add vendor name
4. Click **Submit Reconciliation** button
5. Wait for finance approval

### For Finance Managers

#### Approving Requests

1. Go to **Imprest Request** list
2. Filter: Status = "Pending Approval"
3. Open request
4. Click **Actions** → **Approve**
5. Adjust amount if needed
6. Add comments
7. Approve
   - System automatically creates disbursement entry

#### Reviewing Reconciliations

1. Go to **Imprest Request** list
2. Filter: Reconciliation Status = "Pending Review"
3. Open request
4. Review uploaded receipts
5. Verify amounts and categories
6. Click **Reconciliation** → **Approve Reconciliation**
   - System automatically:
     - Books expenses to GL accounts
     - Handles variance (refund/additional payment)
     - Clears employee advance account

### For Event Managers

#### Track Event Expenses

1. Open **Event Registration**
2. Click **Reports** → **View Event Summary**
3. See all linked imprest requests
4. View category breakdown
5. Monitor budget vs actual

## 💡 Examples

### Example 1: Simple Training Event

**Request:**
```
Employee: John Doe
Event: Leadership Training - Nairobi
Purpose: Training event expenses

Expenses:
- Transport (Taxi): 2 trips × 1500 = 3000
- Meals (Lunch): 2 days × 800 = 1600
- Materials (Handouts): 1 × 5000 = 5000
Total Requested: 9600
```

**Approval:**
```
Finance Manager approves: 9600
System creates:
  DR: John Doe - Advance: 9600
  CR: Main Bank Account: 9600
```

**Reconciliation:**
```
Actual expenses:
- Transport: 2800 (saved 200)
- Meals: 1600
- Materials: 5000
Total Spent: 9400
Variance: +200 (refund to company)

System creates:
  DR: Transport Expense: 2800
  DR: Meals Expense: 1600
  DR: Training Expense: 5000
  CR: John Doe - Advance: 9400

Then handles variance:
  DR: Main Bank Account: 200
  CR: John Doe - Advance: 200
```

### Example 2: Multi-Day Conference

**Request with Event Link:**
```
Employee: Jane Smith
Event: Annual Conference - Mombasa
Purpose: Conference logistics and speaker fees

Expenses:
- Transport: 4 trips × 3000 = 12000
- Accommodation: 3 nights × 8000 = 24000
- Meals: 6 meals × 1200 = 7200
- Venue: 1 × 50000 = 50000
Total Requested: 93200
```

**Event Summary Shows:**
```
Total Imprest for Event: 93200
Category Breakdown:
- Venue: 50000 (53.6%)
- Accommodation: 24000 (25.7%)
- Transport: 12000 (12.9%)
- Meals: 7200 (7.7%)
```

## 🎨 Screenshots & UI

### Dashboard View
```
┌─────────────────────────────────────────────────────────┐
│  Pending Approvals: 5    Pending Reconciliations: 3     │
│  Disbursed (MTD): 450,000    Reconciled (MTD): 380,000  │
│  Outstanding Advances: 70,000                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Expense by Category (This Month)                       │
│  ─────────────────────────────────────────────          │
│  🚗 Transport: 120,000                                  │
│  🏨 Accommodation: 95,000                               │
│  🍽️  Meals: 65,000                                      │
│  📚 Training: 50,000                                    │
│  🎪 Venue: 40,000                                       │
└─────────────────────────────────────────────────────────┘
```

### Report Filters
```
┌─────────────────────────────────────────┐
│  From Date: [01-01-2026]                │
│  To Date: [31-01-2026]                  │
│  Employee: [All]                        │
│  Event: [Leadership Training]           │
│  Status: [Approved]                     │
│  Reconciliation: [Completed]            │
│                                         │
│  [🔍 Apply Filters] [📊 Export]        │
└─────────────────────────────────────────┘
```

## 🔧 Customization

### Adding Custom Categories

```python
# In Imprest Expense Category
category = frappe.new_doc("Imprest Expense Category")
category.category_name = "Entertainment"
category.company = "Your Company"
category.expense_account = "Entertainment Expense - YC"
category.description = "Client entertainment and team building"
category.insert()
```

### Custom Approval Workflow

Create a workflow in Frappe to add:
- Manager approval
- Department head approval
- CFO approval for amounts > 100,000

### Event Budget Enforcement

Add custom script to Event Registration:

```javascript
frappe.ui.form.on('Event Registration', {
    refresh: function(frm) {
        // Show budget vs imprest warning
        if (frm.doc.budget) {
            frappe.call({
                method: 'get_event_imprest_summary',
                args: {event_name: frm.doc.name},
                callback: function(r) {
                    if (r.message.total_approved > frm.doc.budget) {
                        frappe.msgprint({
                            title: 'Budget Exceeded',
                            indicator: 'red',
                            message: `Imprest approved (${r.message.total_approved}) 
                                     exceeds budget (${frm.doc.budget})`
                        });
                    }
                }
            });
        }
    }
});
```

## 📚 API Reference

### WhitelistedMethods

```python
# Submit reconciliation
frappe.call({
    method: 'imprest_request.submit_reconciliation',
    args: {imprest_request: 'IMP-2026-00001'}
})

# Approve reconciliation
frappe.call({
    method: 'imprest_request.approve_reconciliation',
    args: {imprest_request: 'IMP-2026-00001'}
})

# Reject reconciliation
frappe.call({
    method: 'imprest_request.reject_reconciliation',
    args: {
        imprest_request: 'IMP-2026-00001',
        rejection_reason: 'Missing receipts for transport'
    }
})

# Get dashboard data
frappe.call({
    method: 'imprest_request.get_imprest_dashboard_data'
})

# Get event summary
frappe.call({
    method: 'imprest_request.get_event_imprest_summary',
    args: {event_name: 'EVT-2026-00001'}
})
```

## 🛡️ Security & Permissions

### Role Permissions

| Role | Create | Read | Write | Submit | Cancel | Delete |
|------|--------|------|-------|--------|--------|--------|
| Employee | ✓ | Own | Own | ✗ | ✗ | ✗ |
| Accounts User | ✓ | All | All | ✓ | ✗ | ✗ |
| Accounts Manager | ✓ | All | All | ✓ | ✓ | ✓ |

### Field-Level Security

- **Approved Amount**: Only editable by Accounts Manager during approval
- **Accounting Entries**: Read-only, system-generated
- **Workflow State**: Controlled by workflow

## 🐛 Troubleshooting

### Common Issues

**Q: Disbursement entry not created on approval**
```
A: Check:
   1. Approved amount is greater than 0
   2. Source account is set
   3. Employee advance parent account exists in settings
   4. User has permission to create Journal Entry
```

**Q: Cannot submit reconciliation**
```
A: Ensure:
   1. At least one reconciliation item added
   2. All receipts uploaded
   3. Request is in "Approved" state
```

**Q: Variance calculation incorrect**
```
A: Verify:
   1. All reconciliation items have amounts
   2. Refresh the form (Ctrl+R)
   3. Check total_reconciled_amount field
```

**Q: Email notifications not sending**
```
A: Check:
   1. Email settings configured in ERPNext
   2. Finance manager email set in settings
   3. Notification flags enabled in settings
   4. Check Email Queue for errors
```

## 📈 Performance Tips

1. **Archive old requests**: Move completed requests older than 2 years to archive
2. **Optimize images**: Compress receipt images before upload
3. **Batch operations**: Approve multiple requests together when possible
4. **Index fields**: Ensure posting_date, employee, event are indexed
5. **Regular cleanup**: Delete draft requests older than 30 days

## 🤝 Contributing

We welcome contributions! Areas for enhancement:
- [ ] Mobile app integration
- [ ] OCR for receipt scanning
- [ ] Budget enforcement
- [ ] Expense policy engine
- [ ] Integration with travel booking
- [ ] Multi-currency support

## 📄 License

MIT License - Feel free to use and modify

## 🆘 Support

- **Documentation**: See IMPLEMENTATION_GUIDE.md
- **Issues**: GitHub Issues
- **Forum**: Frappe Forum
- **Email**: support@yourcompany.com

## 🎉 Acknowledgments

Built for seamless integration with Event Management module
Designed for efficiency and compliance
Made with ❤️ for the Frappe community

---

**Version**: 1.0.0  
**Last Updated**: January 2026  
**Maintainer**: Your Company
