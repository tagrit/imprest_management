// Imprest Request List View Configuration
// Shows reconciliation status prominently with color indicators
frappe.listview_settings['Imprest Request'] = {
    add_fields: [
        "employee_name", 
        "purpose", 
        "approved_amount", 
        "total_reconciled_amount", 
        "reconciliation_status", 
        "workflow_state", 
        "posting_date", 
        "variance_amount",
        "reconciliation_completed_date"
    ],
    
    get_indicator: function(doc) {
        // Priority: Show reconciliation status for approved imprests
        if (doc.workflow_state === "Approved") {
            
            // Fully reconciled - all done
            if (doc.reconciliation_status === "Fully Reconciled") {
                return [__("Fully Reconciled"), "green", "reconciliation_status,=,Fully Reconciled"];
            } 
            
            // Reconciled but variance needs settlement
            else if (doc.reconciliation_status === "Reconciled - Variance Pending") {
                return [__("Variance Pending"), "orange", "reconciliation_status,=,Reconciled - Variance Pending"];
            } 
            
            // Some items approved, some pending/rejected
            else if (doc.reconciliation_status === "Partially Reconciled") {
                return [__("Partially Reconciled"), "blue", "reconciliation_status,=,Partially Reconciled"];
            } 
            
            // Employee submitted, waiting for finance review
            else if (doc.reconciliation_status === "Pending Review") {
                return [__("Pending Review"), "yellow", "reconciliation_status,=,Pending Review"];
            } 
            
            // Approved but employee hasn't submitted any reconciliation yet
            else {
                return [__("Pending Reconciliation"), "lightblue", "workflow_state,=,Approved"];
            }
        } 
        
        // Not yet approved
        else if (doc.workflow_state === "Pending Approval") {
            return [__("Pending Approval"), "orange", "workflow_state,=,Pending Approval"];
        } 
        
        // Rejected
        else if (doc.workflow_state === "Rejected") {
            return [__("Rejected"), "red", "workflow_state,=,Rejected"];
        } 
        
        // Draft
        else {
            return [__("Draft"), "gray", "docstatus,=,0"];
        }
    },
    
    formatters: {
        approved_amount: function(value, df, doc) {
            return format_currency(value, doc.currency);
        },
        
        total_reconciled_amount: function(value, df, doc) {
            if (!value) return '<span style="color: #999;">-</span>';
            
            let approved = doc.approved_amount || 0;
            let reconciled = value || 0;
            let percentage = approved > 0 ? (reconciled / approved * 100) : 0;
            
            let color = percentage >= 95 ? 'green' : (percentage >= 50 ? 'blue' : 'orange');
            
            return `<span style="color: ${color};">${format_currency(value, doc.currency)}</span> 
                    <small style="color: #999;">(${percentage.toFixed(0)}%)</small>`;
        },
        
        variance_amount: function(value, df, doc) {
            if (!value || Math.abs(value) < 1) {
                return '<span style="color: #999;">-</span>';
            }
            
            let color = value > 0 ? "green" : "red";
            let icon = value > 0 ? "↓" : "↑";
            
            return `<span style="color: ${color}; font-weight: 500;">
                        ${icon} ${format_currency(Math.abs(value), doc.currency)}
                    </span>`;
        },
        
        reconciliation_status: function(value) {
            if (!value) return '<span style="color: #999;">Not Started</span>';
            
            let colors = {
                "Fully Reconciled": "green",
                "Reconciled - Variance Pending": "orange",
                "Partially Reconciled": "blue",
                "Pending Review": "goldenrod"
            };
            
            let color = colors[value] || "#999";
            return `<span style="color: ${color}; font-weight: 500;">${value}</span>`;
        }
    },
    
    onload: function(listview) {
        // Add quick filter buttons
        listview.page.add_inner_button(__('Pending Reconciliation'), function() {
            frappe.set_route('List', 'Imprest Request', {
                'workflow_state': 'Approved',
                'reconciliation_status': ['in', ['', null]]
            });
        }, __('Filters'));
        
        listview.page.add_inner_button(__('Pending Review'), function() {
            frappe.set_route('List', 'Imprest Request', {
                'reconciliation_status': 'Pending Review'
            });
        }, __('Filters'));
        
        listview.page.add_inner_button(__('Variance Pending'), function() {
            frappe.set_route('List', 'Imprest Request', {
                'reconciliation_status': 'Reconciled - Variance Pending'
            });
        }, __('Filters'));
        
        listview.page.add_inner_button(__('Fully Reconciled'), function() {
            frappe.set_route('List', 'Imprest Request', {
                'reconciliation_status': 'Fully Reconciled'
            });
        }, __('Filters'));
    },
    
    // Add bulk actions for Accounts Managers
    button: {
        show: function(doc) {
            return doc.workflow_state === 'Pending Approval';
        },
        get_label: function() {
            return __('Approve');
        },
        get_description: function(doc) {
            return __('Approve for {0}', [format_currency(doc.approved_amount)]);
        },
        action: function(doc) {
            frappe.set_route('Form', 'Imprest Request', doc.name);
        }
    }
};