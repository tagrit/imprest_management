from frappe import _


def get_data():
    return [
        {
            "module_name": "Imprest Management",
            "category": "Modules",
            "label": _("Imprest Management"),
            "color": "#4CAF50",
            "icon": "octicon octicon-credit-card",
            "type": "module",
            "description": "Manage employee cash advances and reconciliations"
        }
    ]
