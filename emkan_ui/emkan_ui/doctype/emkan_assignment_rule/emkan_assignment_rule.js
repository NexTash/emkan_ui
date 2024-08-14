// Copyright (c) 2024, NexTash and contributors
// For license information, please see license.txt

frappe.ui.form.on("Emkan Assignment Rule", {
	doctypes: function(frm) {
        frappe.model.with_doctype(frm.doc.doctypes, function () {
			var options = $.map(frappe.get_meta(frm.doc.doctypes).fields, function (d) {
				if (
					d.fieldname &&
					// d.fieldtype === "Select" &&
					frappe.model.no_value_type.indexOf(d.fieldtype) === -1
				) {
					return d.fieldname;
				}
				return null;
			});
			frm.set_df_property("condition_key", "options", options);
			frm.get_field("condition_key").refresh();
		});
    }
});
