from frappe import _


def get_data():
    return [
        {
            "label": _("Documents"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Imprest Request",
                    "description": _("Employee imprest requests"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Imprest Expense Category",
                    "description": _("Manage expense categories"),
                },
            ]
        },
        {
            "label": _("Reports"),
            "items": [
                {
                    "type": "report",
                    "name": "Imprest Summary Report",
                    "doctype": "Imprest Request",
                    "is_query_report": True,
                },
                {
                    "type": "report",
                    "name": "Event-wise Imprest Report",
                    "doctype": "Imprest Request",
                    "is_query_report": True,
                },
                {
                    "type": "report",
                    "name": "Category-wise Expense Analysis",
                    "doctype": "Imprest Request",
                    "is_query_report": True,
                },
            ]
        },
        {
            "label": _("Setup"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Imprest Management Settings",
                    "description": _("Configure imprest management"),
                },
            ]
        },
    ]
