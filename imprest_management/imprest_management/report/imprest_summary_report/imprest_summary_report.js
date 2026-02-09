// Copyright (c) 2026, Your Company and contributors
// For license information, please see license.txt

frappe.query_reports["Imprest Summary Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee"
        },
        {
            "fieldname": "event",
            "label": __("Event"),
            "fieldtype": "Link",
            "options": "Event Registration"
        },
        {
            "fieldname": "workflow_state",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nDraft\nPending Approval\nApproved\nRejected"
        },
        {
            "fieldname": "reconciliation_status",
            "label": __("Reconciliation Status"),
            "fieldtype": "Select",
            "options": "\nPending Review\nCompleted\nRejected"
        }
    ],
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (column.fieldname == "workflow_state") {
            if (value === "Approved") {
                value = `<span class="indicator-pill green">${value}</span>`;
            } else if (value === "Rejected") {
                value = `<span class="indicator-pill red">${value}</span>`;
            } else if (value === "Pending Approval") {
                value = `<span class="indicator-pill orange">${value}</span>`;
            }
        }
        
        if (column.fieldname == "reconciliation_status") {
            if (value === "Completed") {
                value = `<span class="indicator-pill green">${value}</span>`;
            } else if (value === "Rejected") {
                value = `<span class="indicator-pill red">${value}</span>`;
            } else if (value === "Pending Review") {
                value = `<span class="indicator-pill orange">${value}</span>`;
            }
        }
        
        if (column.fieldname == "variance_amount") {
            if (parseFloat(data.variance_amount) > 0) {
                value = `<span style="color: green;">${value}</span>`;
            } else if (parseFloat(data.variance_amount) < 0) {
                value = `<span style="color: red;">${value}</span>`;
            }
        }
        
        return value;
    },
    
    onload: function(report) {
        // Add custom buttons
        report.page.add_inner_button(__("Imprest Dashboard"), function() {
            frappe.set_route('query-report', 'Imprest Dashboard');
        });
    }
};
