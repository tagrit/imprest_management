# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    
    return columns, data, None, chart


def get_columns():
    return [
        {
            "fieldname": "expense_category",
            "label": _("Expense Category"),
            "fieldtype": "Link",
            "options": "Imprest Expense Category",
            "width": 200
        },
        {
            "fieldname": "sub_category",
            "label": _("Sub Category"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "total_amount",
            "label": _("Total Amount"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "transaction_count",
            "label": _("# of Transactions"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "avg_amount",
            "label": _("Average Amount"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "percentage",
            "label": _("% of Total"),
            "fieldtype": "Percent",
            "width": 120
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    
    # Get reconciled expenses grouped by category and sub-category
    data = frappe.db.sql(f"""
        SELECT 
            ric.expense_category,
            COALESCE(ric.sub_category, 'General') as sub_category,
            SUM(ric.amount) as total_amount,
            COUNT(ric.name) as transaction_count,
            AVG(ric.amount) as avg_amount
        FROM `tabReconciliation Item` ric
        INNER JOIN `tabImprest Request` ir ON ric.parent = ir.name
        WHERE ir.reconciliation_status = 'Completed'
        {conditions}
        GROUP BY ric.expense_category, ric.sub_category
        ORDER BY total_amount DESC
    """, filters, as_dict=1)
    
    # Calculate percentage of total
    total_expenses = sum(flt(d.get("total_amount", 0)) for d in data)
    
    for row in data:
        if total_expenses > 0:
            row.percentage = (flt(row.total_amount) / total_expenses) * 100
        else:
            row.percentage = 0
    
    return data


def get_conditions(filters):
    conditions = ""
    
    if filters.get("from_date"):
        conditions += " AND ir.reconciliation_completed_date >= %(from_date)s"
    
    if filters.get("to_date"):
        conditions += " AND ir.reconciliation_completed_date <= %(to_date)s"
    
    if filters.get("event"):
        conditions += " AND ir.event = %(event)s"
    
    if filters.get("employee"):
        conditions += " AND ir.employee = %(employee)s"
    
    if filters.get("expense_category"):
        conditions += " AND ric.expense_category = %(expense_category)s"
    
    return conditions


def get_chart_data(data):
    if not data:
        return None
    
    # Pie chart showing category distribution
    labels = []
    values = []
    
    # Group by main category (ignore sub-category for chart)
    category_totals = {}
    for row in data:
        category = row.get("expense_category")
        if category not in category_totals:
            category_totals[category] = 0
        category_totals[category] += flt(row.get("total_amount", 0))
    
    # Sort and take top 8
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:8]
    
    for category, amount in sorted_categories:
        labels.append(category)
        values.append(amount)
    
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Expense Amount",
                    "values": values
                }
            ]
        },
        "type": "donut",
        "height": 300,
        "colors": ["#4CAF50", "#2196F3", "#FFC107", "#FF5722", "#9C27B0", "#00BCD4", "#FF9800", "#8BC34A"]
    }
