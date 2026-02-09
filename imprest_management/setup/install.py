import frappe

def after_install():
    """
    Called after app is installed
    """
    frappe.db.commit()
    print("Imprest Management app installed successfully!")