frappe.ui.form.on('Payment Reconciliation', {
    refresh:function(frm){
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
        }
});
