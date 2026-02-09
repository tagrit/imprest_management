# Installation Guide - Imprest Management App

## Overview
Imprest Management is a standalone Frappe app that provides complete cash advance management functionality. It can be installed on any Frappe/ERPNext site.

## Prerequisites

- Frappe Framework version 14.0 or higher
- ERPNext (optional, but recommended for accounting features)
- Python 3.10+
- MariaDB 10.3+ or PostgreSQL 12+

## Installation Steps

### Method 1: Install from GitHub (Recommended)

```bash
# Navigate to your bench directory
cd frappe-bench

# Get the app
bench get-app https://github.com/your-org/imprest_management.git

# Install on your site
bench --site [your-site-name] install-app imprest_management

# Migrate the database
bench --site [your-site-name] migrate

# Clear cache and rebuild
bench --site [your-site-name] clear-cache
bench build --app imprest_management

# Restart bench
bench restart
```

### Method 2: Install from Local Directory

```bash
# Navigate to your bench directory
cd frappe-bench

# Copy the app to apps directory
cp -r /path/to/imprest_management ./apps/

# Install on your site
bench --site [your-site-name] install-app imprest_management

# Migrate and rebuild
bench --site [your-site-name] migrate
bench build --app imprest_management
bench restart
```

### Method 3: Development Installation

```bash
# Navigate to bench apps directory
cd frappe-bench/apps

# Clone or copy the app
git clone https://github.com/your-org/imprest_management.git
# OR
cp -r /path/to/imprest_management .

# Install in development mode
cd ../
bench --site [your-site-name] install-app imprest_management

# Enable developer mode (optional)
bench --site [your-site-name] set-config developer_mode 1

# Watch for changes (optional)
bench watch
```

## Post-Installation Setup

### Step 1: Verify Installation

```bash
# Check if app is installed
bench --site [your-site-name] list-apps

# You should see:
# frappe
# erpnext (if installed)
# imprest_management ✓
```

Login to your site and verify:
1. Go to **Module List** - You should see "Imprest Management"
2. Go to **DocType List** - Search for "Imprest Request"
3. Go to **Report** - Search for "Imprest Summary Report"

### Step 2: Run Initial Setup

The app includes an automatic setup wizard that runs on first install. However, you can manually run it:

```bash
# Open Frappe console
bench --site [your-site-name] console

# Run setup
>>> from imprest_management.setup.install.after_install import execute
>>> execute()
```

This will:
- Create sample expense categories
- Setup employee advance accounts
- Configure default settings
- Create sample data (optional)

### Step 3: Configure Settings

1. Navigate to: **Imprest Management > Setup > Imprest Management Settings**

2. Configure the following:

   **Account Settings:**
   ```
   Employee Advance Parent Account: Employee Advances - [Your Company]
   Default Source Account: [Your main bank account]
   Default Company: [Your Company Name]
   Default Cost Center: [Optional]
   ```

   **Notification Settings:**
   ```
   Finance Manager Email: finance@yourcompany.com
   ☑ Send Approval Notifications
   ☑ Send Reconciliation Notifications
   ```

   **Approval Settings:**
   ```
   Auto Approve Threshold: 5000 (optional)
   ☑ Require Manager Approval
   ```

3. **Save** the settings

### Step 4: Create Expense Categories

Navigate to: **Imprest Management > Documents > Imprest Expense Category**

Create categories (if not auto-created):

| Category Name | Expense Account | Company |
|--------------|-----------------|---------|
| Transport | Transport Expense - [Company] | [Your Company] |
| Accommodation | Lodging Expense - [Company] | [Your Company] |
| Meals & Refreshments | Food & Beverage Expense - [Company] | [Your Company] |
| Training Materials | Training Expense - [Company] | [Your Company] |
| Host Stay | Entertainment Expense - [Company] | [Your Company] |

### Step 5: Setup Chart of Accounts

Ensure these accounts exist in your Chart of Accounts:

```
Assets
└── Current Assets
    └── Employee Advances (Group Account)
        └── [Employee Name] - Advance (Auto-created per employee)

Expenses
└── Operating Expenses
    ├── Transport Expense
    ├── Accommodation Expense / Lodging Expense
    ├── Food & Beverage Expense
    ├── Training Expense
    ├── Entertainment Expense
    └── Miscellaneous Expense
```

**To create missing accounts:**

1. Go to: **Accounting > Chart of Accounts**
2. Right-click on "Operating Expenses"
3. Add Child → Enter account name
4. Account Type: "Expense Account"
5. Save

### Step 6: Setup Permissions (Optional)

The app comes with default permissions. To customize:

1. Go to: **Settings > Role Permissions Manager**
2. Select: **Imprest Request**
3. Adjust permissions as needed:
   - Employee: Create, Read (own only), Write (own only)
   - Accounts User: Full access except Delete
   - Accounts Manager: Full access

### Step 7: Test the System

Create a test imprest request:

1. Go to: **Imprest Management > Documents > Imprest Request**
2. Click **New**
3. Fill in:
   - Employee: [Select employee]
   - Purpose: "Test imprest request"
   - Source Account: [Select bank account]
4. Add Expense Items:
   - Category: Transport
   - Description: "Test transport"
   - Quantity: 1
   - Rate: 1000
5. **Save**
6. As Accounts Manager, **Approve** the request
7. Verify disbursement journal entry created
8. Add reconciliation items
9. Submit reconciliation
10. Approve reconciliation
11. Verify expense entries created

## Integration with Event Management

If you have an Event Management module installed:

1. The "Event" field in Imprest Request will link to "Event Registration"
2. You can track all imprest per event
3. Event-wise reports will show comprehensive cost analysis

To integrate:
- Ensure Event Registration doctype exists
- Link imprest requests to events
- Use "Event-wise Imprest Report" for analysis

## Troubleshooting Installation

### Issue: App not showing in module list

**Solution:**
```bash
bench --site [your-site-name] clear-cache
bench --site [your-site-name] reload-doc imprest_management imprest_management module_def
bench restart
```

### Issue: DocTypes not appearing

**Solution:**
```bash
# Reload all doctypes
bench --site [your-site-name] migrate
bench --site [your-site-name] clear-cache
bench build --app imprest_management
```

### Issue: Permission denied errors

**Solution:**
```bash
# Set correct permissions
bench --site [your-site-name] set-admin-password [password]
# Login as Administrator and setup permissions
```

### Issue: Accounting entries not creating

**Check:**
1. Source account is set in Imprest Request
2. Employee advance parent account exists in settings
3. User has permission to create Journal Entry
4. Company default currency is set

### Issue: Email notifications not working

**Check:**
1. Email Account is setup (Settings > Email Account)
2. SMTP settings are correct
3. Finance manager email is set in settings
4. Check Email Queue for errors

## Updating the App

```bash
# Navigate to bench
cd frappe-bench

# Pull latest changes
cd apps/imprest_management
git pull origin main

# Go back to bench root
cd ../..

# Migrate
bench --site [your-site-name] migrate

# Build
bench build --app imprest_management

# Restart
bench restart
```

## Uninstalling the App

```bash
# Backup first!
bench --site [your-site-name] backup

# Uninstall app
bench --site [your-site-name] uninstall-app imprest_management

# Remove app from bench
bench remove-app imprest_management
```

## Production Deployment

### Using Supervisor

```bash
# Setup production
bench setup production [your-user]

# Enable supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart all
```

### Using systemd

```bash
# Generate systemd files
sudo bench setup systemd

# Enable and start
sudo systemctl enable frappe-bench-frappe-web frappe-bench-frappe-worker@*
sudo systemctl start frappe-bench-frappe-web frappe-bench-frappe-worker@*
```

### Using nginx

```bash
# Setup nginx
sudo bench setup nginx

# Restart nginx
sudo service nginx reload
```

## Database Backups

```bash
# Manual backup
bench --site [your-site-name] backup

# Automated backups (cron)
# Add to crontab:
0 2 * * * cd /path/to/frappe-bench && /path/to/bench --site [your-site-name] backup
```

## Performance Optimization

After installation, optimize performance:

```bash
# Add database indexes
bench --site [your-site-name] mariadb

# Run these SQL commands:
ALTER TABLE `tabImprest Request` ADD INDEX idx_employee (employee);
ALTER TABLE `tabImprest Request` ADD INDEX idx_event (event);
ALTER TABLE `tabImprest Request` ADD INDEX idx_posting_date (posting_date);
ALTER TABLE `tabImprest Request` ADD INDEX idx_workflow_state (workflow_state);
```

## Support & Resources

- **Documentation**: See README.md in the app root
- **GitHub Issues**: https://github.com/your-org/imprest_management/issues
- **Frappe Forum**: https://discuss.frappe.io
- **Email Support**: support@yourcompany.com

## Next Steps

After successful installation:

1. ✅ Review **README.md** for features overview
2. ✅ Check **IMPLEMENTATION_GUIDE.md** for detailed configuration
3. ✅ Train your employees on creating requests
4. ✅ Train finance team on approvals
5. ✅ Create your first real imprest request
6. ✅ Run reports to see analytics

**Congratulations! Your Imprest Management system is ready to use!** 🎉

---

**Version**: 1.0.0  
**Last Updated**: January 29, 2026  
**Minimum Frappe Version**: 14.0.0
