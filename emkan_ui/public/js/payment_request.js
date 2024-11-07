frappe.ui.form.on('Payment Request', {
    onload: function(frm) {
        if (frm.doc.message && frm.doc.message.includes("Thank you for your business!")) {
            frm.set_value('message', ''); 
        }
    }
});
