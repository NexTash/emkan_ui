// Copyright (c) 2025, NexTash and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Rejoining', {
    employee: function(frm) {
        if (frm.doc.employee) {
            frappe.db.get_list('Leave Application', {
                filters: {
                    employee: frm.doc.employee,
                    status: 'Approved',
                    leave_type: 'Annual Leave (Encashment)'
                },
                fields: ['from_date', 'to_date'],
                order_by: 'creation desc',
                limit: 1
            }).then(result => {
                if (result.length > 0) {
                    let leave = result[0];

                    frm.set_value('leave_start_date', leave.from_date);
                    frm.set_value('expected_end_date', leave.to_date);

                    // Calculate days difference
                    const diff = frappe.datetime.get_diff(leave.to_date, leave.from_date) + 1;
                    frm.set_value('leave_days', diff);
                } else {
                    frappe.msgprint('No Approved Leave Application found with Leave Type "Annual Leave (Encashment)" for this employee');
                    frm.set_value('leave_start_date', '');
                    frm.set_value('expected_end_date', '');
                    frm.set_value('leave_days', '');
                }
            });
        }
    },

    return: function(frm) {
        if (frm.doc.return) {
            frm.set_df_property('return_date', 'hidden', 0);
        } else {
            frm.set_df_property('return_date', 'hidden', 1);
            frm.set_value('return_date', '');
        }
    },

    refresh: function(frm) {
        // Apply visibility on refresh
        if (frm.doc.return) {
            frm.set_df_property('return_date', 'hidden', 0);
        } else {
            frm.set_df_property('return_date', 'hidden', 1);
        }
    }
});
