
import frappe

def after_install():

    """

    Called after the app is installed

    """

    frappe.db.commit()

    print("Imprest Management app installed successfully!")

