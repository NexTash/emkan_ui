frappe.ui.form.on("Material Request", {
    onload: function(frm) {
        frappe.call({
            method: 'emkan_ui.events.workflow.role_assign_by_user',
            args: {
                doc: frm.doc,  
            },
            callback: function(r) {
                if (r.message) {
                  
                    frm.set_query('custom_assigned_to', () => {
                        return {
                            filters: {
                                name: ['in', r.message]  
                            }
                        };
                    });
                }
                console.log(r.message);
            }
        });
    }
});
ch