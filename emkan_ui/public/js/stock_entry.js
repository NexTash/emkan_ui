
frappe.ui.form.on("Stock Entry", {
    validate(frm, dt, dn){
        if(frm.doc.stock_entry_type == "Material Issue"){
            for(let row of frm.doc.items){
                if (frm.doc.custom_account) {
                    frappe.model.set_value(row.doctype, row.name, "expense_account", frm.doc.custom_account)
                }

                if (frm.doc.custom_account) {
                    frappe.model.set_value(row.doctype, row.name, "cost_center", frm.doc.custom_cost_center)
                }
            }
        }
    }
})