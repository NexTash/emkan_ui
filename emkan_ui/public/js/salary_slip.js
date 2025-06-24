frappe.ui.form.on('Salary Slip', {
    employee: function(frm) {
        if (!frm.doc.employee) return;

        setTimeout(() => {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Leave Application",
                    filters: {
                        employee: frm.doc.employee,
                        status: "Approved",
                        leave_type: "Annual Leave (Encashment)"
                    },
                    fields: ["name", "from_date", "to_date", "total_leave_days"],
                    order_by: "creation desc",
                    limit: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        const leave = r.message[0];

                        setTimeout(() => {
                            frm.set_value('start_date', leave.from_date);
                            frm.set_value('end_date', leave.to_date);
                            frm.set_value('custom_leave_settlement_paid_days', leave.total_leave_days);
                        }, 500);
                    } else {
                        setTimeout(() => {
                            frm.set_value('start_date', null);
                            frm.set_value('end_date', null);
                            frm.set_value('custom_leave_settlement_paid_days', 0);
                        }, 500);
                    }
                }
            });
        }, 700);
    }
});