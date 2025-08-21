frappe.ui.form.on('Payment Request Reference', {
    references_add: function(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, 'reference_doctype', 'Purchase Invoice');
        recalc(frm);
    },
    reference_name: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row) return;

        if (row.reference_doctype === 'Purchase Invoice' && row.reference_name) {
            frappe.call({
                method: 'frappe.client.get',
                args: { doctype: 'Purchase Invoice', name: row.reference_name, fields: ['bill_no'] },
                callback: function(r) {
                    const bill = r.message ? (r.message.bill_no || '') : '';
                    frappe.model.set_value(cdt, cdn, 'bill_no', bill);
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, 'bill_no', '');
        }
    }
});

frappe.ui.form.on('Custom Payment Request', {
    party: function(frm) {
        if (!frm.doc.party) return;
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Purchase Invoice',
                filters: {
                    supplier: frm.doc.party,
                    outstanding_amount: ['>', 0],
                    docstatus: 1,
                    status: ['!=', 'Paid'],
                    is_return: 0
                },
                fields: ['name', 'outstanding_amount', 'bill_no'],
                limit_page_length: 100
            },
            callback: function(r) {
                frm.clear_table('references');
                (r.message || []).forEach(inv => {
                    let row = frm.add_child('references');
                    row.reference_doctype = 'Purchase Invoice';
                    row.reference_name = inv.name;
                    row.amount = flt(inv.outstanding_amount);
                    row.supplier_invoice_number = inv.bill_no || '';
                });
                frm.refresh_field('references');
                recalc(frm);
            }
        });
    }
});

function recalc(frm) {
    let total = 0;
    (frm.doc.references || []).forEach(r => total += flt(r.amount || 0));
    frm.set_value('grand_total', total);
}
