# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_report_summary(data)
    
    return columns, data, None, chart, summary


def get_columns():
    return [
        {
            "fieldname": "name",
            "label": _("Request ID"),
            "fieldtype": "Link",
            "options": "Imprest Request",
            "width": 150
        },
        {
            "fieldname": "posting_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "employee_name",
            "label": _("Employee"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "event",
            "label": _("Event"),
            "fieldtype": "Link",
            "options": "Event Registration",
            "width": 150
        },
        {
            "fieldname": "purpose",
            "label": _("Purpose"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "total_requested_amount",
            "label": _("Requested"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "approved_amount",
            "label": _("Approved"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "total_reconciled_amount",
            "label": _("Reconciled"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "variance_amount",
            "label": _("Variance"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "workflow_state",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "reconciliation_status",
            "label": _("Reconciliation"),
            "fieldtype": "Data",
            "width": 120
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    
    data = frappe.db.sql(f"""
        SELECT 
            name,
            posting_date,
            employee_name,
            event,
            purpose,
            total_requested_amount,
            approved_amount,
            total_reconciled_amount,
            variance_amount,
            workflow_state,
            reconciliation_status
        FROM `tabImprest Request`
        WHERE 1=1 {conditions}
        ORDER BY posting_date DESC
    """, filters, as_dict=1)
    
    return data


def get_conditions(filters):
    conditions = ""
    
    if filters.get("from_date"):
        conditions += " AND posting_date >= %(from_date)s"
    
    if filters.get("to_date"):
        conditions += " AND posting_date <= %(to_date)s"
    
    if filters.get("employee"):
        conditions += " AND employee = %(employee)s"
    
    if filters.get("event"):
        conditions += " AND event = %(event)s"
    
    if filters.get("workflow_state"):
        conditions += " AND workflow_state = %(workflow_state)s"
    
    if filters.get("reconciliation_status"):
        conditions += " AND reconciliation_status = %(reconciliation_status)s"
    
    return conditions


def get_chart_data(data):
    # Chart showing approved vs reconciled amounts
    labels = []
    approved_amounts = []
    reconciled_amounts = []
    
    for row in data[:10]:  # Show top 10
        labels.append(row.get("name"))
        approved_amounts.append(flt(row.get("approved_amount", 0)))
        reconciled_amounts.append(flt(row.get("total_reconciled_amount", 0)))
    
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Approved Amount",
                    "values": approved_amounts
                },
                {
                    "name": "Reconciled Amount",
                    "values": reconciled_amounts
                }
            ]
        },
        "type": "bar",
        "height": 300,
        "colors": ["#4CAF50", "#2196F3"]
    }


def get_report_summary(data):
    if not data:
        return []
    
    total_requested = sum(flt(d.get("total_requested_amount", 0)) for d in data)
    total_approved = sum(flt(d.get("approved_amount", 0)) for d in data)
    total_reconciled = sum(flt(d.get("total_reconciled_amount", 0)) for d in data)
    total_variance = sum(flt(d.get("variance_amount", 0)) for d in data)
    
    pending_count = sum(1 for d in data if d.get("workflow_state") == "Pending Approval")
    approved_count = sum(1 for d in data if d.get("workflow_state") == "Approved")
    
    return [
        {
            "value": total_requested,
            "label": "Total Requested",
            "datatype": "Currency",
            "indicator": "Blue"
        },
        {
            "value": total_approved,
            "label": "Total Approved",
            "datatype": "Currency",
            "indicator": "Green"
        },
        {
            "value": total_reconciled,
            "label": "Total Reconciled",
            "datatype": "Currency",
            "indicator": "Green"
        },
        {
            "value": total_variance,
            "label": "Total Variance",
            "datatype": "Currency",
            "indicator": "Orange" if total_variance != 0 else "Green"
        },
        {
            "value": pending_count,
            "label": "Pending Approval",
            "indicator": "Orange"
        },
        {
            "value": approved_count,
            "label": "Approved",
            "indicator": "Green"
        }
    ]
