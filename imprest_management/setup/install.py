import frappe
from frappe.core.doctype.data_import.data_import import import_file

def after_install():
    """Load fixtures after installation"""
    try:
        # Import workflow states
        import_file("imprest_management", "fixtures/workflow_state.json")
        
        # Import workflows
        import_file("imprest_management", "fixtures/workflow.json")
        
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Error loading fixtures: {str(e)}")