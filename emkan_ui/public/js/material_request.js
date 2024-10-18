frappe.ui.form.on('Material Request', {
    cost_center: function(frm) {
        let department = frm.doc.cost_center;

        frm.doc.items.forEach(function(item) {
            item.cost_center = department;
        });

        frm.refresh_field('items');
    },

    custom_project: function(frm) {
        let project = frm.doc.custom_project;

        frm.doc.items.forEach(function(item) {
            item.project = project;
        });

        frm.refresh_field('items');
    },
    custom_department(frm, dt, dn){
        frappe.call({
            method: 'emkan_ui.events.mapping.mapping_cost_center',
            args: {
                division: frm.doc.custom_department
            },
            callback: (r) => {
                frappe.model.set_value(dt, dn, "cost_center", r.message)  
            }
        })
    }
});
