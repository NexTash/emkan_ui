frappe.ui.form.on('Payment Request', {
    onload: function(frm) {
        if (frm.doc.message === 'Default Text') {  // Replace 'Default Text' with the actual default value
            frm.set_value('message', '');
        }
    }
});
