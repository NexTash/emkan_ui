frappe.ui.form.on("Purchase Order", {
    custom_department(frm, dt, dn){
        if(frm.doc.custom_department == "BSI"){
            frappe.model.set_value(dt, dn, "custom_prefix", "BSI-")
        }
        else{
            frappe.model.set_value(dt, dn, "custom_prefix", "EE-S-")
        }
    }
});