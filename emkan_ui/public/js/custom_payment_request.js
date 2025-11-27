// Child table: Payment Request Reference
frappe.ui.form.on('Payment Request Reference', {
    // When new row added
    references_add: function(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, 'reference_doctype', 'Purchase Invoice');
        recalc(frm);
    },

    // When row deleted
    references_remove: function(frm) {
        recalc(frm);
    },

    // When reference_name is changed
    reference_name: function(frm, cdt, cdn) {
        const row = locals[cdt] && locals[cdt][cdn];
        if (!row) return;

        if (row.reference_doctype === 'Purchase Invoice' && row.reference_name) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Purchase Invoice',
                    name: row.reference_name,
                    fields: ['bill_no', 'outstanding_amount', 'bill_date']   // ✅ added bill_date
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'bill_no', r.message.bill_no || '');
                        frappe.model.set_value(cdt, cdn, 'custom_supplier_invoice_date', r.message.bill_date || '');   // ✅ set date in child
                        if (typeof r.message.outstanding_amount !== 'undefined') {
                            frappe.model.set_value(cdt, cdn, 'amount', flt(r.message.outstanding_amount));
                        }
                    } else {
                        frappe.model.set_value(cdt, cdn, 'bill_no', '');
                        frappe.model.set_value(cdt, cdn, 'custom_supplier_invoice_date', '');
                    }
                    recalc(frm);
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, 'bill_no', '');
            frappe.model.set_value(cdt, cdn, 'custom_supplier_invoice_date', '');
            recalc(frm);
        }
    },

    // When amount changed
    amount: function(frm) {
        recalc(frm);
    }
});


// Parent doctype: Custom Payment Request
frappe.ui.form.on('Custom Payment Request', {
    onload: function(frm) {
        recalc(frm);
    },
    refresh: function(frm) {
        recalc(frm);
    },
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
                fields: ['name', 'outstanding_amount', 'bill_no', 'bill_date'], // ✅ fetch bill_date
                order_by: 'bill_date asc', // ✅ show old invoices first
                limit_page_length: 500
            },
            callback: function(r) {
                frm.clear_table('references');
                (r.message || []).forEach(function(inv) {
                    let row = frm.add_child('references');
                    row.reference_doctype = 'Purchase Invoice';
                    row.reference_name = inv.name;
                    row.custom_supplier_invoice_date = inv.bill_date || '';
                    row.amount = flt(inv.outstanding_amount);
                    row.supplier_invoice_number = inv.bill_no || '';
                });
                frm.refresh_field('references');
                recalc(frm);
            }
        });
    }
});


// Central calc function
function recalc(frm) {
    let total = 0;
    (frm.doc.references || []).forEach(r => {
        total += flt(r.amount || 0);
    });
    frm.set_value('grand_total', parseFloat(total.toFixed(2)));
}
