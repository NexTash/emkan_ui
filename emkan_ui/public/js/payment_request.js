frappe.ui.form.on('Payment Request', {
    onload: function(frm) {
        if (frm.doc.message && frm.doc.message.includes("Thank you for your business!")) {
            frm.set_value('message', ''); 
        }
    }
});


frappe.ui.form.on('Payment Request', {
    onload: function (frm) {
        // Populate Party Name if Party Type and Party are already selected
        if (frm.doc.party_type && frm.doc.party) {
            fetch_party_name(frm);
        }
    },
    party: function (frm) {
        // Fetch Party Name when Party is selected
        fetch_party_name(frm);
    },
    party_type: function (frm) {
        // Clear Party and Party Name when Party Type is changed
        frm.set_value('party', null);
        frm.set_value('party_name', null);
    }
});

// Function to fetch Party Name based on Party Type and Party
function fetch_party_name(frm) {
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
                frm.set_value('party_name', r[doctype.toLowerCase() + '_name'] || r.name); // Fallback to `name` if `*_name` doesn't exist
            });
        }
    }
}


