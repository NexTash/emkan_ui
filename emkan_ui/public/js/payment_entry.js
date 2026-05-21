frappe.ui.form.on("Payment Entry", {
    onload(frm, dt, dn){
		if(frm.doc.custom_department == "EMKAN-4 (BSI) - EECS"){
			frappe.model.set_value(dt, dn, "custom_prefix", "BSI-")
		}
        else if(frm.doc.custom_department == "Al Maha"){
            frappe.model.set_value(dt, dn, "custom_prefix", "EMK-ALM-")
        }
		else{
			frappe.model.set_value(dt, dn, "custom_prefix", "EE-S-")
		}
    },
    custom_department(frm, dt, dn){
        if(frm.doc.custom_department == "EMKAN-4 (BSI) - EECS"){
            frappe.model.set_value(dt, dn, "custom_prefix", "BSI-")
        }
        else if(frm.doc.custom_department == "Al Maha"){
            frappe.model.set_value(dt, dn, "custom_prefix", "EMK-ALM-")
        }
        else{
            frappe.model.set_value(dt, dn, "custom_prefix", "EE-S-")
        }
    },
    payment_type(frm, dt, dn){
        get_account(frm, dt, dn)
    },
    party_type(frm, dt, dn){
        get_account(frm, dt, dn)
    },
    custom_advance_payment(frm, dt, dn){
        get_account(frm, dt, dn)
    },
    validate(frm, dt, dn){
        get_account(frm, dt, dn)
    },
});

function get_account(frm, dt, dn){
    if(frm.doc.payment_type == "Pay" && frm.doc.party_type == "Supplier" && frm.doc.custom_advance_payment){
        frappe.db.get_doc('Company', frm.doc.company)
        .then(doc => {
            frappe.model.set_value(dt, dn, "paid_to", doc.default_advance_paid_account)
        })
    }
    else if(frm.doc.payment_type == "Receive" && frm.doc.party_type == "Customer" && frm.doc.custom_advance_payment){
        frappe.db.get_doc('Company', frm.doc.company)
        .then(doc => {
            frappe.model.set_value(dt, dn, "paid_from", doc.default_advance_received_account)
        })
    }
}
