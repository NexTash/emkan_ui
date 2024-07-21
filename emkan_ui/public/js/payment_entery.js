frappe.ui.form.on("Payment Entry", {
    party_type: function(frm) {
        if (frm.doc.custom_advance_payment && frm.doc.party_type === "Supplier") {
            frm.set_value('paid_to', 'Advance To Supplier - EE');
            frm.refresh();
        } 
        else if (frm.doc.custom_advance_payment && frm.doc.party_type === "Customer") {
            frm.set_value('paid_from', 'Advance From Customer - EE');
            frm.refresh();
        } 
    }
});
