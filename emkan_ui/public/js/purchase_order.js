frappe.ui.form.on("Purchase Order", {
    custom_department(frm, dt, dn){
        if(frm.doc.custom_department == "BSI"){
            frappe.model.set_value(dt, dn, "naming_series", "BSI-.YY.-")
        }
        else{
            frappe.model.set_value(dt, dn, "naming_series", "EE-S-.YY.-")
        }
    }
});