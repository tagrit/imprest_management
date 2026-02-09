# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    
    return columns, data, None, chart


def get_columns():
    return [
        {
            "fieldname": "event",
            "label": _("Event"),
            "fieldtype": "Link",
            "options": "Event Registration",
            "width": 200
        },
        {
            "fieldname": "event_name",
            "label": _("Event Name"),
            "fieldtype": "Data",
            "width": 250
        },
        {
            "fieldname": "event_date",
            "label": _("Event Date"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "request_count",
            "label": _("# of Requests"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "total_approved",
            "label": _("Total Approved"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "total_spent",
            "label": _("Total Spent"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "balance",
            "label": _("Balance"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "completion_rate",
            "label": _("Completion %"),
            "fieldtype": "Percent",
            "width": 120
        }
    ]


def get_data(filters):
    # Get all events with imprest requests
    data = frappe.db.sql("""
        SELECT 
            ir.event,
            er.event_name,
            er.start_date as event_date,
            COUNT(ir.name) as request_count,
            SUM(ir.approved_amount) as total_approved,
            SUM(CASE 
                WHEN ir.reconciliation_status = 'Completed' 
                THEN ir.total_reconciled_amount 
                ELSE 0 
            END) as total_spent,
            SUM(ir.approved_amount) - SUM(CASE 
                WHEN ir.reconciliation_status = 'Completed' 
                THEN ir.total_reconciled_amount 
                ELSE 0 
            END) as balance
        FROM `tabImprest Request` ir
        LEFT JOIN `tabEvent Registration` er ON ir.event = er.name
        WHERE ir.event IS NOT NULL 
        AND ir.event != ''
        AND ir.workflow_state = 'Approved'
        GROUP BY ir.event, er.event_name, er.start_date
        ORDER BY er.start_date DESC
    """, as_dict=1)
    
    # Calculate completion rate
    for row in data:
        if row.total_approved and row.total_approved > 0:
            row.completion_rate = (flt(row.total_spent) / flt(row.total_approved)) * 100
        else:
            row.completion_rate = 0
    
    return data


def get_chart_data(data):
    if not data:
        return None
    
    # Top 10 events by approved amount
    top_events = sorted(data, key=lambda x: flt(x.get("total_approved", 0)), reverse=True)[:10]
    
    labels = []
    approved = []
    spent = []
    
    for event in top_events:
        labels.append(event.get("event_name", "")[:30])  # Truncate long names
        approved.append(flt(event.get("total_approved", 0)))
        spent.append(flt(event.get("total_spent", 0)))
    
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Approved",
                    "values": approved
                },
                {
                    "name": "Spent",
                    "values": spent
                }
            ]
        },
        "type": "bar",
        "height": 300,
        "colors": ["#4CAF50", "#2196F3"]
    }
