frappe.ui.form.on('Payment Request Reference', {
    references_add: function(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, 'reference_doctype', 'Purchase Invoice');
        recalc(frm);
    },

    references_remove: function(frm) {
        recalc(frm);
    },

    reference_name: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];

        if (row.reference_doctype === 'Purchase Invoice' && row.reference_name) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Purchase Invoice',
                    name: row.reference_name,
                    fields: ['bill_no', 'outstanding_amount']
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'supplier_invoice_number', r.message.bill_no || '');
                        frappe.model.set_value(cdt, cdn, 'amount', flt(r.message.outstanding_amount) || 0);
                    } else {
                        frappe.model.set_value(cdt, cdn, 'supplier_invoice_number', '');
                        frappe.model.set_value(cdt, cdn, 'amount', 0);
                    }
                    recalc(frm);
                }
            });
        } else if (row.reference_doctype === 'Journal Entry' && row.reference_name) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Journal Entry',
                    name: row.reference_name,
                    fields: ['name', 'bill_no'],
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.call({
                            method: 'frappe.client.get_list',
                            args: {
                                doctype: 'Journal Entry Account',
                                filters: { parent: r.message.name },
                                fields: ['party_type', 'party', 'debit', 'credit']
                            },
                            callback: function(res) {
                                if (res.message && res.message.length) {
                                    let accounts = res.message;
                                    let last_row = accounts[accounts.length - 1];

                                    if (last_row.party_type === 'Supplier' && last_row.party === frm.doc.party) {
                                        let total = (last_row.debit || 0) - (last_row.credit || 0);
                                        frappe.model.set_value(cdt, cdn, 'supplier_invoice_number', r.message.bill_no || '');
                                        frappe.model.set_value(cdt, cdn, 'amount', flt(total));
                                    } else {
                                        frappe.model.set_value(cdt, cdn, 'supplier_invoice_number', '');
                                        frappe.model.set_value(cdt, cdn, 'amount', 0);
                                    }
                                }
                                recalc(frm);
                            }
                        });
                    } else {
                        frappe.model.set_value(cdt, cdn, 'supplier_invoice_number', '');
                        frappe.model.set_value(cdt, cdn, 'amount', 0);
                        recalc(frm);
                    }
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, 'supplier_invoice_number', '');
            frappe.model.set_value(cdt, cdn, 'amount', 0);
            recalc(frm);
        }
    },

    amount: function(frm) {
        recalc(frm);
    }
});

frappe.ui.form.on('Custom Payment Request', {
    onload: function(frm) {
        recalc(frm);
    },
    refresh: function(frm) {
        recalc(frm);
    },
    party: function(frm) {
        if (!frm.doc.party) return;

        frm.clear_table("references");

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
                fields: ['name', 'outstanding_amount', 'bill_no']
            },
            callback: function(r) {
                (r.message || []).forEach(function(inv) {
                    let row = frm.add_child('references');
                    row.reference_doctype = 'Purchase Invoice';
                    row.reference_name = inv.name;
                    row.supplier_invoice_number = inv.bill_no || '';
                    row.amount = flt(inv.outstanding_amount);
                });

                frappe.call({
                    method: 'emkan_ui.emkan_ui.doctype.custom_payment_request.custom_payment_request.get_supplier_journal_entries',
                    args: { supplier: frm.doc.party },
                    callback: function(r2) {
                        (r2.message || []).forEach(function(je) {
                            let row = frm.add_child('references');
                            row.reference_doctype = 'Journal Entry';
                            row.reference_name = je.name;
                            row.supplier_invoice_number = je.bill_no || '';
                            row.amount = flt(je.amount);
                        });

                        frm.refresh_field('references');
                        recalc(frm);
                    }
                });
            }
        });
    }
});

function recalc(frm) {
    let total = 0;
    (frm.doc.references || []).forEach(r => {
        total += flt(r.amount || 0);
    });
    frm.set_value('grand_total', parseFloat(total.toFixed(2)));
}