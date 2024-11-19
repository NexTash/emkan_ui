frappe.ui.form.on('Payment Request', {
    onload: function(frm) {
        if (frm.doc.message && frm.doc.message.includes("Thank you for your business!")) {
            frm.set_value('message', ''); 
        }
    }
});



frappe.ui.form.on('Payment Request', {
    party: function (frm) {
        if (frm.doc.party_type && frm.doc.party) {
            let doctype_map = {
                'Customer': 'Customer',
                'Supplier': 'Supplier',
                'Employee': 'Employee',
                'Shareholder': 'Shareholder'
            };

            let doctype = doctype_map[frm.doc.party_type];
            if (doctype) {
                frappe.db.get_value(doctype, frm.doc.party, doctype.toLowerCase() + '_name', (r) => {
                    frm.set_value('party_name', r[doctype.toLowerCase() + '_name'] || r.name); // Fallback to name if *_name doesn't exist
                });
            }
        } else {
            frm.set_value('party_name', null);
        }
    },
    party_type: function (frm) {
        // Clear party_name and party when party type is changed
        frm.set_value('party_name', null);
        frm.set_value('party', null);
    }
});