frappe.ui.form.on('Payment Reconciliation', {
    refresh:function(frm){
        if (frm.doc.party_type === "Supplier" && frm.doc.invoices && frm.doc.invoices.length) {
            frm.doc.invoices.forEach(async (row) => {
                if (!row.supplier_invoice_number && row.invoice) {
                    let invoiceDoc = await frappe.db.get_doc('Purchase Invoice', row.invoice);
                    if (invoiceDoc && invoiceDoc.supplier_invoice_number) {
                        frappe.model.set_value(row.doctype, row.name, 'supplier_invoice_number', invoiceDoc.supplier_invoice_number);
                    }
                }
            });
            frm.refresh_field('invoices');
        }
        let promises = frm.doc.invoices.map((row, index) => {
                if(row.invoice_type === "Purchase Invoice") {
                    return frappe.db.get_value("Purchase Invoice", row.invoice_number, 'bill_no')
                        .then(r => {
                            if(r.message && r.message.bill_no) {
                                frm.doc.invoices[index].custom_bill_no = r.message.bill_no;
                            }
                        });
                } else {
                    return Promise.resolve();
                }
            });
            Promise.all(promises).then(() => {
                frm.refresh_field("invoices");
            });
        if (!frm.doc.payments || !frm.doc.payments.length) return;
        frm.doc.payments.forEach(async (row) => {
            try {
                if ((row.reference_type || '').toString().trim() === 'Payment Entry' && row.reference_name) {
                    const pe = await frappe.db.get_doc('Payment Entry', row.reference_name);

                    const refs = Array.isArray(pe.references) ? pe.references : [];

                    const poNames = refs
                        .filter(r => ((r.reference_doctype || r.reference_type) === 'Purchase Order'))
                        .map(r => (r.reference_name || r.reference || r.reference_no || '').toString().trim())
                        .filter(Boolean);

                    const unique = [...new Set(poNames)];
                    const value = unique.length ? unique.join(', ') : '';

                    frappe.model.set_value(row.doctype, row.name, 'custom_po_number', value);
                } else {
                    frappe.model.set_value(row.doctype, row.name, 'custom_po_number', '');
                }
            } catch (err) {
                console.error('Error populating custom_po_number for row', row, err);
                frappe.model.set_value(row.doctype, row.name, 'custom_po_number', '');
            }
        });

        frm.refresh_field('payments');
        }
});
