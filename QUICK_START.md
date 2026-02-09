# Quick Start Guide - Imprest Management

Get up and running in **10 minutes**! ⚡

## Prerequisites Check

```bash
# Check Frappe version (should be >= 14.0)
bench version

# Check if you have a site
bench --site [your-site] console
>>> frappe.__version__
# Should show 14.x or 15.x
```

## Installation (3 minutes)

### Step 1: Get the App

```bash
cd frappe-bench
bench get-app https://github.com/your-org/imprest_management.git
```

### Step 2: Install on Site

```bash
bench --site [your-site-name] install-app imprest_management
```

### Step 3: Restart

```bash
bench restart
```

**✅ Installation Complete!**

## Setup (5 minutes)

### Step 1: Login

Navigate to: `http://[your-site]:8000`

Login with your Administrator credentials

### Step 2: Open Module

Go to: **Module List** → **Imprest Management**

### Step 3: Configure Settings

Click: **Imprest Management Settings**

Fill in:
```
Employee Advance Parent Account: Employee Advances - [Company]
Finance Manager Email: finance@yourcompany.com
```

Click **Save**

### Step 4: Verify Categories

Go to: **Imprest Expense Category**

You should see auto-created categories:
- Transport
- Accommodation
- Meals & Refreshments
- Training Materials
- Host Stay

**✅ Setup Complete!**

## First Request (2 minutes)

### Step 1: Create Request

1. Go to: **Imprest Request** → **New**
2. Select: Your employee
3. Purpose: "Test request"
4. Source Account: [Your bank]
5. Add expense item:
   - Category: Transport
   - Description: "Test"
   - Quantity: 1
   - Rate: 1000
6. **Save**

### Step 2: Approve

1. Switch to Accounts Manager user (or Admin)
2. Open the request
3. Click: **Actions** → **Approve**
4. Approved Amount: 1000
5. **Approve**

### Step 3: Check Accounting

Go to: **Journal Entry** → Find the disbursement entry

Should see:
```
DR: [Employee] - Advance    1000
    CR: Bank                     1000
```

**✅ System Working!**

## Next Steps

### Explore Reports

1. **Imprest Summary Report** - Overview of all requests
2. **Event-wise Imprest Report** - Track by event
3. **Category-wise Expense** - Spending patterns

### Create Real Request

1. Link to an event (if you have Event Management)
2. Add multiple expense items
3. Go through full workflow:
   - Request → Approve → Spend → Upload Receipts → Reconcile

### Customize

1. Add your own expense categories
2. Set up approval workflows
3. Configure email templates
4. Create custom reports

## Common Tasks

### Add New Category

```
1. Go to: Imprest Expense Category → New
2. Category Name: "Communication"
3. Expense Account: "Telephone Expense - [Company]"
4. Save
```

### View Dashboard

```
1. Go to: Imprest Management module
2. See summary cards
3. Click on reports
```

### Upload Receipt

```
1. Open approved imprest request
2. Scroll to: Reconciliation section
3. Add row:
   - Category: [Select]
   - Amount: [Enter]
   - Receipt: [Upload file]
4. Click: Submit Reconciliation
```

## Troubleshooting

### Can't see module?

```bash
bench --site [site] clear-cache
bench restart
```

### Permission issues?

```
Login as Administrator
Go to: Role Permissions Manager
Select: Imprest Request
Grant permissions to required roles
```

### No expense accounts?

```
1. Go to: Chart of Accounts
2. Right-click: Operating Expenses
3. Add Child
4. Create accounts for each category
```

## Help & Support

- **Full Docs**: See README.md
- **Detailed Setup**: See INSTALLATION.md
- **Configuration**: See IMPLEMENTATION_GUIDE.md
- **Deployment**: See DEPLOYMENT_CHECKLIST.md

## Success Checklist

After 10 minutes, you should have:

- ✅ App installed
- ✅ Settings configured
- ✅ Categories created
- ✅ Test request created
- ✅ Approval working
- ✅ Accounting entries verified
- ✅ Ready for production use!

**Congratulations! You're all set!** 🎉

---

**Need Help?**
- Email: support@yourcompany.com
- Forum: https://discuss.frappe.io
- GitHub: https://github.com/your-org/imprest_management
