import frappe

def after_install():
    """Called after app is installed"""
    frappe.db.commit()
