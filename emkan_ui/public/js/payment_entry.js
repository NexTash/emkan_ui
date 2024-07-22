frappe.ui.form.on("Payment Entry", {
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
