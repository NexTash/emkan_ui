frappe.ui.form.on('Material Request', {
    custom_cost_center: function(frm) {
        let department = frm.doc.custom_cost_center;

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
    }
});
