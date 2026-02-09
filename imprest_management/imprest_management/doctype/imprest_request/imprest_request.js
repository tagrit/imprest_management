// SIMPLIFIED VARIANCE HANDLING UI
// Changes:
// 1. Removed complex variance resolution dialog
// 2. Added "Create Variance JE" button that redirects to Journal Entry form
// 3. Added validation warnings for reconciliation amount
// 4. Simplified workflow

frappe.ui.form.on('Imprest Request', {
    onload: function(frm) {
        if (frm.is_new() && !frm.doc.source_account) {
            frappe.db.get_single_value('Imprest Management Settings', 'default_source_account')
                .then(default_account => {
                    if (default_account) {
                        frm.set_value('source_account', default_account);
                    }
                });
        }
    },
    
    refresh: function(frm) {
        // === Approval Buttons ===
        if (frm.doc.workflow_state === 'Pending Approval' && frappe.user_roles.includes('Accounts Manager')) {
            frm.add_custom_button(__('Approve'), function() {
                approve_imprest(frm);
            }, __('Actions')).addClass('btn-primary');
            
            frm.add_custom_button(__('Reject'), function() {
                reject_imprest(frm);
            }, __('Actions')).addClass('btn-danger');
        }
        
        // === Employee Reconciliation Buttons ===
        if (frm.doc.workflow_state === 'Approved' && frm.doc.docstatus === 1 && !frm.doc.reconciliation_status) {
            frm.add_custom_button(__('Submit Reconciliation'), function() {
                submit_reconciliation(frm);
            }).addClass('btn-primary');
        }
        
        if (frm.doc.workflow_state === 'Approved' && frm.doc.docstatus === 1 && 
            (frm.doc.reconciliation_status === 'Partially Reconciled' || frm.doc.reconciliation_status === 'Pending Review')) {
            if (!frappe.user_roles.includes('Accounts Manager')) {
                frm.add_custom_button(__('Submit Additional Receipts'), function() {
                    submit_additional_reconciliation(frm);
                }).addClass('btn-primary');
            }
        }
        
        // === Finance Manager Reconciliation Buttons ===
        if (frm.doc.reconciliation_status === 'Pending Review' && frappe.user_roles.includes('Accounts Manager')) {
            frm.add_custom_button(__('Approve All Items'), function() {
                approve_reconciliation(frm);
            }, __('Reconciliation')).addClass('btn-primary');
            
            frm.add_custom_button(__('Approve Selected Items'), function() {
                approve_selected_reconciliation_items(frm);
            }, __('Reconciliation')).addClass('btn-success');
            
            frm.add_custom_button(__('Reject Selected Items'), function() {
                reject_selected_reconciliation_items(frm);
            }, __('Reconciliation')).addClass('btn-danger');
        }
        
        if (frm.doc.reconciliation_status === 'Partially Reconciled' && frappe.user_roles.includes('Accounts Manager')) {
            frm.add_custom_button(__('Approve Selected Items'), function() {
                approve_selected_reconciliation_items(frm);
            }, __('Reconciliation')).addClass('btn-success');
            
            frm.add_custom_button(__('Reject Selected Items'), function() {
                reject_selected_reconciliation_items(frm);
            }, __('Reconciliation')).addClass('btn-danger');
        }
        
        // === SIMPLIFIED VARIANCE RESOLUTION - CREATE JE BUTTON ===
        if (frm.doc.reconciliation_status === 'Reconciled - Variance Pending' && 
            frappe.user_roles.includes('Accounts Manager')) {
            
            frm.add_custom_button(__('Create Variance JE'), function() {
                create_variance_journal_entry(frm);
            }).addClass('btn-warning');
        }
        
        
        // Color code statuses
        color_code_status(frm);
        
        // Update reconciliation summary
        update_reconciliation_summary(frm);
        
        // Show variance instructions if there's a variance
        show_variance_instructions(frm);
    },
    
    employee: function(frm) {
        if (frm.doc.employee) {
            frappe.db.get_value('Employee', frm.doc.employee, ['employee_name', 'company'], function(r) {
                if (r) {
                    frm.set_value('employee_name', r.employee_name);
                    if (!frm.doc.company) {
                        frm.set_value('company', r.company);
                    }
                }
            });
        }
    },
    
    event: function(frm) {
        if (frm.doc.event) {
            frappe.db.get_value('Event Registration', frm.doc.event, 
                ['event_name', 'event_location', 'organization_name'], 
                function(r) {
                    if (r && !frm.doc.purpose) {
                        frm.set_value('purpose', 
                            `Event: ${r.event_name} at ${r.event_location} for ${r.organization_name}`);
                    }
                }
            );
        }
    },
    
    before_save: function(frm) {
        calculate_expense_totals(frm);
        validate_reconciliation_total(frm);
    }
});

frappe.ui.form.on('Imprest Expense Item', {
    quantity: function(frm, cdt, cdn) {
        calculate_line_amount(frm, cdt, cdn);
    },
    
    rate: function(frm, cdt, cdn) {
        calculate_line_amount(frm, cdt, cdn);
    },
    
    expense_items_remove: function(frm) {
        calculate_expense_totals(frm);
    }
});

frappe.ui.form.on('Reconciliation Item', {
    reconciliation_items_add: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.reconciliation_status) {
            frappe.model.set_value(cdt, cdn, 'reconciliation_status', 'Pending');
        }
    },
    
    amount: function(frm, cdt, cdn) {
        update_reconciliation_summary(frm);
        validate_reconciliation_total(frm);
    },
    
    reconciliation_items_remove: function(frm) {
        update_reconciliation_summary(frm);
    }
});

// === Helper Functions ===

function calculate_line_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    row.amount = (row.quantity || 0) * (row.rate || 0);
    frm.refresh_field('expense_items');
    calculate_expense_totals(frm);
}

function calculate_expense_totals(frm) {
    let total = 0;
    if (frm.doc.expense_items) {
        frm.doc.expense_items.forEach(function(item) {
            total += (item.amount || 0);
        });
    }
    frm.set_value('total_requested_amount', total);
    
    if (!frm.doc.approved_amount) {
        frm.set_value('approved_amount', total);
    }
}

function validate_reconciliation_total(frm) {
    /**
     * VALIDATION: Warn user if reconciliation items exceed approved amount
     */
    if (!frm.doc.reconciliation_items || !frm.doc.approved_amount) {
        return;
    }
    
    let total_reconciliation = 0;
    frm.doc.reconciliation_items.forEach(function(item) {
        total_reconciliation += (item.amount || 0);
    });
    
    let approved = frm.doc.approved_amount || 0;
    
    if (total_reconciliation > approved) {
        frappe.show_alert({
            message: __('⚠️ Warning: Reconciliation total ({0}) exceeds approved amount ({1})', 
                [format_currency(total_reconciliation), format_currency(approved)]),
            indicator: 'red'
        }, 10);
    } else if (total_reconciliation > (approved - 50)) {
        frappe.show_alert({
            message: __('⚠️ Reconciliation total is very close to approved limit'),
            indicator: 'orange'
        }, 5);
    }
}

function update_reconciliation_summary(frm) {
    if (!frm.doc.reconciliation_items || frm.doc.reconciliation_items.length === 0) {
        return;
    }
    
    let total_submitted = 0;
    let total_approved = 0;
    let total_pending = 0;
    let total_rejected = 0;
    
    let count_approved = 0;
    let count_pending = 0;
    let count_rejected = 0;
    
    frm.doc.reconciliation_items.forEach(function(item) {
        total_submitted += (item.amount || 0);
        
        if (item.reconciliation_status === 'Approved') {
            total_approved += (item.amount || 0);
            count_approved++;
        } else if (item.reconciliation_status === 'Rejected') {
            total_rejected += (item.amount || 0);
            count_rejected++;
        } else {
            total_pending += (item.amount || 0);
            count_pending++;
        }
    });
    
    let summary_html = `
        <div class="reconciliation-summary" style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h5 style="margin-top: 0;">Reconciliation Summary</h5>
            <div class="row">
                <div class="col-md-3">
                    <strong>Total Submitted:</strong><br>
                    ${format_currency(total_submitted)}
                </div>
                <div class="col-md-3">
                    <strong>Approved (${count_approved}):</strong><br>
                    <span style="color: green;">${format_currency(total_approved)}</span>
                </div>
                <div class="col-md-3">
                    <strong>Pending (${count_pending}):</strong><br>
                    <span style="color: orange;">${format_currency(total_pending)}</span>
                </div>
                <div class="col-md-3">
                    <strong>Rejected (${count_rejected}):</strong><br>
                    <span style="color: red;">${format_currency(total_rejected)}</span>
                </div>
            </div>
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #dee2e6;">
                <strong>Official Reconciled:</strong> ${format_currency(frm.doc.total_reconciled_amount || 0)}<br>
                <strong>Variance:</strong> ${format_currency(frm.doc.variance_amount || 0)}
            </div>
        </div>
    `;
    
    if (frm.fields_dict.reconciliation_summary_html) {
        frm.set_df_property('reconciliation_summary_html', 'options', summary_html);
    }
}

function show_variance_instructions(frm) {
    /**
     * Show helpful instructions when there's a variance
     */
    if (frm.doc.reconciliation_status === 'Reconciled - Variance Pending' && 
        Math.abs(frm.doc.variance_amount || 0) >= 1.0) {
        
        let variance = frm.doc.variance_amount || 0;
        let is_underspent = variance > 0;
        
        let instructions_html = `
            <div class="alert alert-${is_underspent ? 'success' : 'warning'}" style="margin: 15px 0;">
                <h5><strong>${is_underspent ? '💰 Employee Underspent' : '⚠️ Employee Overspent'}</strong></h5>
                <p><strong>Approved:</strong> ${format_currency(frm.doc.approved_amount)}</p>
                <p><strong>Spent:</strong> ${format_currency(frm.doc.total_reconciled_amount)}</p>
                <p><strong>Variance:</strong> <span style="font-size: 1.2em;">${format_currency(Math.abs(variance))}</span></p>
                <hr>
                <h6><strong>📝 How to Resolve:</strong></h6>
                ${is_underspent ? `
                    <p><strong>Employee needs to refund ${format_currency(Math.abs(variance))}</strong></p>
                    <p>Click "Create Variance JE" button above and create a Journal Entry:</p>
                    <ul>
                        <li><strong>If cash refund:</strong> Dr. Cash Account | Cr. ${frm.doc.employee_name} - Advance</li>
                        <li><strong>If bank transfer:</strong> Dr. Bank Account | Cr. ${frm.doc.employee_name} - Advance</li>
                        <li><strong>If salary deduction:</strong> Dr. Salary Payable | Cr. ${frm.doc.employee_name} - Advance</li>
                    </ul>
                ` : `
                    <p><strong>Company needs to pay employee ${format_currency(Math.abs(variance))}</strong></p>
                    <p>Click "Create Variance JE" button above and create a Journal Entry:</p>
                    <ul>
                        <li><strong>If justified overspending:</strong> Dr. Expense Account(s) | Cr. Bank Account</li>
                        <li><strong>If clearing advance:</strong> Dr. ${frm.doc.employee_name} - Advance | Cr. Bank Account</li>
                    </ul>
                `}
                <p style="margin-top: 10px;"><em>💡 The button will pre-fill the Journal Entry form with relevant details.</em></p>
            </div>
        `;
        
        // Show in a dedicated field or dashboard section
        if (frm.fields_dict.variance_instructions_html) {
            frm.set_df_property('variance_instructions_html', 'options', instructions_html);
        } else {
            // Show as alert if field doesn't exist
            frm.dashboard.add_comment(instructions_html, null, true);
        }
    }
}

function color_code_status(frm) {
    if (frm.doc.workflow_state === 'Approved') {
        frm.get_field('workflow_state').$wrapper.css('color', 'green');
    } else if (frm.doc.workflow_state === 'Rejected') {
        frm.get_field('workflow_state').$wrapper.css('color', 'red');
    }
    
    if (frm.doc.reconciliation_status === 'Fully Reconciled') {
        frm.get_field('reconciliation_status').$wrapper.css('color', 'green');
    } else if (frm.doc.reconciliation_status === 'Reconciled - Variance Pending') {
        frm.get_field('reconciliation_status').$wrapper.css('color', 'orange');
    } else if (frm.doc.reconciliation_status === 'Partially Reconciled') {
        frm.get_field('reconciliation_status').$wrapper.css('color', 'blue');
    } else if (frm.doc.reconciliation_status === 'Pending Review') {
        frm.get_field('reconciliation_status').$wrapper.css('color', 'orange');
    }
}

// === Approval Functions ===

function approve_imprest(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Approve Imprest Request'),
        fields: [
            {
                fieldname: 'approved_amount',
                fieldtype: 'Currency',
                label: __('Approved Amount'),
                default: frm.doc.total_requested_amount,
                reqd: 1
            },
            {
                fieldname: 'approval_comments',
                fieldtype: 'Small Text',
                label: __('Comments')
            }
        ],
        primary_action_label: __('Approve'),
        primary_action: function(values) {
            frm.set_value('approved_amount', values.approved_amount);
            frm.set_value('approval_comments', values.approval_comments);
            frm.set_value('workflow_state', 'Approved');
            frm.set_value('approver', frappe.session.user);
            frm.set_value('approval_date', frappe.datetime.now_datetime());
            
            frm.save().then(() => {
                frappe.msgprint(__('Imprest approved. Reconciliation items auto-populated.'));
                d.hide();
                frm.reload_doc();
            });
        }
    });
    d.show();
}

function reject_imprest(frm) {
    frappe.prompt([
        {
            fieldname: 'rejection_reason',
            fieldtype: 'Small Text',
            label: __('Rejection Reason'),
            reqd: 1
        }
    ], function(values) {
        frm.set_value('workflow_state', 'Rejected');
        frm.set_value('approval_comments', values.rejection_reason);
        frm.set_value('approver', frappe.session.user);
        frm.set_value('approval_date', frappe.datetime.now_datetime());
        
        frm.save().then(() => {
            frappe.msgprint(__('Imprest rejected'));
        });
    }, __('Reject Imprest Request'));
}

// === Reconciliation Functions ===

function submit_reconciliation(frm) {
    if (!frm.doc.reconciliation_items || frm.doc.reconciliation_items.length === 0) {
        frappe.msgprint(__('Please add at least one reconciliation item'));
        return;
    }
    
    let has_pending = false;
    frm.doc.reconciliation_items.forEach(function(item) {
        if (item.reconciliation_status === 'Pending') {
            has_pending = true;
        }
    });
    
    if (!has_pending) {
        frappe.msgprint(__('No pending items to submit'));
        return;
    }
    
    frappe.call({
        method: 'imprest_management.imprest_management.doctype.imprest_request.imprest_request.submit_reconciliation',
        args: {
            imprest_request: frm.doc.name
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                frm.reload_doc();
                frappe.msgprint(__('Reconciliation submitted'));
            }
        }
    });
}

function submit_additional_reconciliation(frm) {
    let pending_count = 0;
    frm.doc.reconciliation_items.forEach(function(item) {
        if (item.reconciliation_status === 'Pending') {
            pending_count++;
        }
    });
    
    if (pending_count === 0) {
        frappe.msgprint(__('Please add new reconciliation items first'));
        return;
    }
    
    frappe.confirm(
        __('Submit {0} new receipt(s) for review?', [pending_count]),
        function() {
            frappe.call({
                method: 'imprest_management.imprest_management.doctype.imprest_request.imprest_request.submit_reconciliation',
                args: {
                    imprest_request: frm.doc.name
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frm.reload_doc();
                        frappe.msgprint(__('Additional receipts submitted'));
                    }
                }
            });
        }
    );
}

function approve_reconciliation(frm) {
    frappe.confirm(
        __('Approve ALL reconciliation items?'),
        function() {
            frappe.call({
                method: 'imprest_management.imprest_management.doctype.imprest_request.imprest_request.approve_reconciliation',
                args: {
                    imprest_request: frm.doc.name
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frm.reload_doc();
                        frappe.msgprint(__('All items approved'));
                    }
                }
            });
        }
    );
}

function approve_selected_reconciliation_items(frm) {
    let selected_items = [];
    let grid = frm.fields_dict.reconciliation_items.grid;
    
    grid.grid_rows.forEach(function(row) {
        if (row.doc.__checked && row.doc.reconciliation_status === 'Pending') {
            selected_items.push(row.doc.name);
        }
    });
    
    if (selected_items.length === 0) {
        frappe.msgprint(__('Select at least one pending item'));
        return;
    }
    
    frappe.confirm(
        __('Approve {0} selected item(s)?', [selected_items.length]),
        function() {
            frappe.call({
                method: 'imprest_management.imprest_management.doctype.imprest_request.imprest_request.approve_reconciliation_items',
                args: {
                    imprest_request: frm.doc.name,
                    item_names: selected_items
                },
                freeze: true,
                freeze_message: __('Processing...'),
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frm.reload_doc();
                        frappe.show_alert({
                            message: __('Approved {0} items', [r.message.approved_items]),
                            indicator: 'green'
                        }, 5);
                    }
                }
            });
        }
    );
}

function reject_selected_reconciliation_items(frm) {
    let selected_items = [];
    let grid = frm.fields_dict.reconciliation_items.grid;
    
    grid.grid_rows.forEach(function(row) {
        if (row.doc.__checked && row.doc.reconciliation_status === 'Pending') {
            selected_items.push(row.doc.name);
        }
    });
    
    if (selected_items.length === 0) {
        frappe.msgprint(__('Select at least one pending item'));
        return;
    }
    
    frappe.prompt([
        {
            fieldname: 'rejection_reason',
            fieldtype: 'Small Text',
            label: __('Rejection Reason'),
            reqd: 1
        }
    ], function(values) {
        frappe.call({
            method: 'imprest_management.imprest_management.doctype.imprest_request.imprest_request.reject_reconciliation_items',
            args: {
                imprest_request: frm.doc.name,
                item_names: selected_items,
                rejection_reason: values.rejection_reason
            },
            freeze: true,
            freeze_message: __('Processing...'),
            callback: function(r) {
                if (r.message && r.message.success) {
                    frm.reload_doc();
                    frappe.show_alert({
                        message: __('Rejected {0} items', [r.message.rejected_items]),
                        indicator: 'red'
                    }, 5);
                }
            }
        });
    }, __('Reject Selected Items'));
}

// === SIMPLIFIED VARIANCE RESOLUTION ===

function create_variance_journal_entry(frm) {
    /**
     * Create Journal Entry for variance settlement
     * Opens JE form with pre-filled values and helpful instructions
     */
    
    let variance = frm.doc.variance_amount || 0;
    let is_underspent = variance > 0;
    let variance_abs = Math.abs(variance);
    
    // Build helpful user remark with instructions
    let user_remark = `Variance settlement for Imprest ${frm.doc.name}
    
Employee: ${frm.doc.employee_name}
Approved: ${format_currency(frm.doc.approved_amount)}
Spent: ${format_currency(frm.doc.total_reconciled_amount)}
Variance: ${format_currency(variance_abs)} (${is_underspent ? 'UNDERSPENT - Employee refunds' : 'OVERSPENT - Company pays'})

${is_underspent ? `
EMPLOYEE REFUND OPTIONS:
1. Cash: Dr. Cash Account | Cr. ${frm.doc.employee_name} - Advance
2. Bank: Dr. Bank Account | Cr. ${frm.doc.employee_name} - Advance  
3. Salary: Dr. Salary Payable | Cr. ${frm.doc.employee_name} - Advance
` : `
COMPANY PAYMENT OPTIONS:
1. Justified Expense: Dr. Expense Account(s) | Cr. Bank Account
2. Clear Advance: Dr. ${frm.doc.employee_name} - Advance | Cr. Bank Account
`}

⚠️ Important: Adjust accounts below based on actual payment method used.`;

    // Get employee advance account name
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: 'Account',
            filters: {
                'account_name': ['like', `${frm.doc.employee_name} - Advance%`],
                'company': frm.doc.company
            },
            fieldname: 'name'
        },
        callback: function(r) {
            let employee_advance_account = r.message ? r.message.name : null;
            
            // Open new Journal Entry form
            frappe.route_options = {
                'company': frm.doc.company,
                'posting_date': frappe.datetime.get_today(),
                'user_remark': user_remark,
                'imprest_request': frm.doc.name
            };
            
            frappe.new_doc('Journal Entry');
            
            // Show instructions dialog
            frappe.msgprint({
                title: __('Creating Variance Journal Entry'),
                message: `
                    <p><strong>Variance Amount: ${format_currency(variance_abs)}</strong></p>
                    <p><strong>Type: ${is_underspent ? 'Employee Refund' : 'Company Payment'}</strong></p>
                    <hr>
                    <p>A new Journal Entry form has been opened with pre-filled details.</p>
                    <p><strong>Please add the accounting entries based on your payment method.</strong></p>
                    ${employee_advance_account ? `<p><em>Employee Advance Account: ${employee_advance_account}</em></p>` : ''}
                `,
                indicator: 'blue'
            });
        }
    });
}

// === Reports ===

function show_event_summary(frm) {
    frappe.call({
        method: 'imprest_management.imprest_management.doctype.imprest_request.imprest_request.get_event_imprest_summary',
        args: {
            event_name: frm.doc.event
        },
        callback: function(r) {
            if (r.message) {
                show_event_summary_dialog(r.message, frm.doc.event);
            }
        }
    });
}

function show_event_summary_dialog(data, event_name) {
    let html = `
        <div class="event-summary">
            <h4>Event: ${event_name}</h4>
            <div class="row">
                <div class="col-md-4">
                    <div class="alert alert-info">
                        <strong>Total Approved:</strong><br>
                        ${format_currency(data.total_approved)}
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="alert alert-success">
                        <strong>Total Spent:</strong><br>
                        ${format_currency(data.total_spent)}
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="alert alert-warning">
                        <strong>Balance:</strong><br>
                        ${format_currency(data.balance)}
                    </div>
                </div>
            </div>
            
            <h5>Requests</h5>
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>Request ID</th>
                        <th>Employee</th>
                        <th class="text-right">Approved</th>
                        <th class="text-right">Spent</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.requests.map(r => `
                        <tr>
                            <td><a href="/app/imprest-request/${r.name}">${r.name}</a></td>
                            <td>${r.employee_name}</td>
                            <td class="text-right">${format_currency(r.approved_amount)}</td>
                            <td class="text-right">${format_currency(r.total_reconciled_amount || 0)}</td>
                            <td>${r.reconciliation_status || 'Pending'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    let d = new frappe.ui.Dialog({
        title: __('Event Imprest Summary'),
        fields: [
            {
                fieldname: 'summary_html',
                fieldtype: 'HTML',
                options: html
            }
        ],
        size: 'extra-large'
    });
    
    d.$wrapper.find('.modal-dialog').css({
        'max-width': '90%',
        'width': '90%'
    });
    
    d.show();
}