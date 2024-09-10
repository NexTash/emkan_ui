frappe.ui.form.on("Material Request", {
	validate(frm, dt, dn){
		frm.add_child("custom_workflow_status", {
            workflow_states : frm.doc.workflow_state,
            approved_by : frappe.session.user
        })
        frm.refresh_field("custom_workflow_status")
    },
});