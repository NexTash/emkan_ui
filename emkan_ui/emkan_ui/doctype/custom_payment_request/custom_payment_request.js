cur_frm.add_fetch("payment_gateway_account", "payment_account", "payment_account");
cur_frm.add_fetch("payment_gateway_account", "payment_gateway", "payment_gateway");
cur_frm.add_fetch("payment_gateway_account", "message", "message");

frappe.ui.form.on("Custom Payment Request", {
	setup: function (frm) {
		frm.set_query("party_type", function () {
			return {
				query: "erpnext.setup.doctype.party_type.party_type.get_party_type",
			};
		});
	},
});

frappe.ui.form.on("Custom Payment Request", "onload", function (frm, dt, dn) {
	if (frm.doc.reference_doctype) {
		frappe.call({
			method: "emkan_ui.emkan_ui.doctype.custom_payment_request.custom_payment_request.get_print_format_list",
			args: { ref_doctype: frm.doc.reference_doctype },
			callback: function (r) {
				set_field_options("print_format", r.message["print_format"]);
			},
		});
	}
});

frappe.ui.form.on("Custom Payment Request", "refresh", function (frm) {
	if (
		frm.doc.payment_request_type == "Inward" &&
		frm.doc.payment_channel !== "Phone" &&
		!["Initiated", "Paid"].includes(frm.doc.status) &&
		!frm.doc.__islocal &&
		frm.doc.docstatus == 1
	) {
		frm.add_custom_button(__("Resend Payment Email"), function () {
			frappe.call({
				method: "emkan_ui.emkan_ui.doctype.custom_payment_request.custom_payment_request.resend_payment_email",
				args: { docname: frm.doc.name },
				freeze: true,
				freeze_message: __("Sending"),
				callback: function (r) {
					if (!r.exc) {
						frappe.msgprint(__("Message Sent"));
					}
				},
			});
		});
	}
});

frappe.ui.form.on("Custom Payment Request", {
    refresh: function (frm) {
        if (
            frm.doc.payment_request_type === "Outward" &&
            ["Initiated", "Partially Paid"].includes(frm.doc.status) &&
            frm.doc.docstatus === 1
        ) {
            frappe.db.get_list("Payment Entry Reference", {
                filters: {
                    custom_custom_payment_request: frm.doc.name
                },
                fields: ["parent", "allocated_amount"]
            }).then(refs => {
                let total_paid = 0;
                if (refs && refs.length) {
                    total_paid = refs.reduce((sum, row) => sum + (row.allocated_amount || 0), 0);
                }

                let request_amount = frm.doc.grand_total || 0;

                if (total_paid < request_amount) {
                    frm.add_custom_button(__("Create Payment Entries"), function () {
                        make_payment_entry(frm);
                    }).addClass("btn-primary");
                }
            });
        }
    },
    party: function (frm) {
        if (frm.doc.party_type === "Supplier" && frm.doc.party) {
            frappe.db.get_value("Supplier", frm.doc.party, "supplier_name", function (r) {
                if (r && r.supplier_name) {
                    frm.set_value("party_name", r.supplier_name);
                }
            });
        }
    }
});

function make_payment_entry(frm) {
    frappe.call({
        method: "emkan_ui.emkan_ui.doctype.custom_payment_request.custom_payment_request.make_payment_entry",
        args: { docname: frm.doc.name },
        freeze: true,
        callback: function (r) {
            if (r.exc) {
                frappe.msgprint(__('Error creating Payment Entry.'));
                return;
            }

            let msg = r.message;
            frm.set_value("reference_doctype", msg.doctype);
            frm.set_value("reference_name", msg.name);
            frm.save('Update');

            if (Array.isArray(msg) && msg.length) {
                frappe.set_route("Form", msg[0].doctype, msg[0].name);
                frappe.msgprint(__("{0} Payment Entries created.", [msg.length]));
                return;
            }

            if (msg && typeof msg === "object" && msg.name) {
                frappe.set_route("Form", msg.doctype || "Payment Entry", msg.name);
                frappe.msgprint(__("Payment Entry {0} created (status: {1}).", [msg.name, msg.docstatus]));
                return;
            }

            frappe.msgprint(__("No Payment Entry created."));
        }
    });
}


function create_payment_entry(frm) {
    frappe.call({
        method: "emkan_ui.emkan_ui.doctype.custom_payment_request.custom_payment_request.make_payment_entry",
        args: { docname: frm.doc.name },
        freeze: true,
        callback: function (r) {
            if (r.exc) {
                frappe.msgprint(__('Error creating Payment Entry.'));
                return;
            }

            let msg = r.message;
            frm.set_value("reference_doctype", msg.doctype);
            frm.set_value("reference_name", msg.name);
            frm.save('Update');

            if (Array.isArray(msg) && msg.length) {
                frappe.set_route("Form", msg[0].doctype, msg[0].name);
                frappe.msgprint(__("{0} Payment Entries created.", [msg.length]));
                return;
            }

            if (msg && typeof msg === "object" && msg.name) {
                frappe.set_route("Form", msg.doctype || "Payment Entry", msg.name);
                frappe.msgprint(__("Payment Entry {0} created (status: {1}).", [msg.name, msg.docstatus]));
                return;
            }

            frappe.msgprint(__("No Payment Entry created."));
        }
    });
}


frappe.ui.form.on("Custom Payment Request", "is_a_subscription", function (frm) {
	frm.toggle_reqd("payment_gateway_account", frm.doc.is_a_subscription);
	frm.toggle_reqd("subscription_plans", frm.doc.is_a_subscription);

	if (frm.doc.is_a_subscription && frm.doc.reference_doctype && frm.doc.reference_name) {
		frappe.call({
			method: "emkan_ui.emkan_ui.doctype.custom_payment_request.custom_payment_request.get_subscription_details",
			args: { reference_doctype: frm.doc.reference_doctype, reference_name: frm.doc.reference_name },
			freeze: true,
			callback: function (data) {
				if (!data.exc) {
					$.each(data.message || [], function (i, v) {
						var d = frappe.model.add_child(
							frm.doc,
							"Subscription Plan Detail",
							"subscription_plans"
						);
						d.qty = v.qty;
						d.plan = v.plan;
					});
					frm.refresh_field("subscription_plans");
				}
			},
		});
	}
});