frappe.ui.form.on('Payment Request', {
    onload: function(frm) {
        if (frm.is_new() && frm.doc.message) {
            frm.set_value('message', '');
        }
    }
});
