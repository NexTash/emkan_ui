frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        frm.add_custom_button('Assign Leave Policy', function() {
            frappe.call({
                method: 'emkan_ui.events.employee.assign_leave_policy',
                args: {
                    employee: frm.doc.name
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(r.message);
                    } else {
                        frappe.msgprint('No message returned.');
                    }
                }
            });
        });
    }
});
