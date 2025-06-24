frappe.ui.form.on("Leave Application", {
    to_date(frm) {
        if (frm.doc.custom_is_leave_settlement && frm.doc.to_date) {
            let to_date = frappe.datetime.add_days(frm.doc.to_date, 1);
            frm.set_value("custom_rejoin_date", to_date);
        }
    },
    custom_is_leave_settlement(frm) {
        if (frm.doc.custom_is_leave_settlement && frm.doc.to_date) {
            let to_date = frappe.datetime.add_days(frm.doc.to_date, 1);
            frm.set_value("custom_rejoin_date", to_date);
        } else {
            frm.set_value("custom_rejoin_date", null);
        }
    }
});
