frappe.ui.form.on('Salary Slip', {
    employee: function(frm) {
        if (!frm.doc.employee) return;

        frappe.call({
            method: "emkan_ui.events.salary_slip.get_encashment_leave",
            args: {
                employee: frm.doc.employee
            },
            callback: function(r) {
                if (r.message && r.message.from_date) {
                    frm.set_value('start_date', r.message.from_date);
                    frm.set_value('end_date', r.message.to_date);
                    frm.set_value('custom_leave_settlement_paid_days', r.message.total_leave_days);
                    frm.set_value('salary_structure', "Leave Settlement");
                } else {
                    frappe.msgprint("No approved 'Annual Leave (Encashment)' found for this employee.");
                    frm.set_value('custom_leave_settlement_paid_days', 0);
                }
            }
        });
    }
});
