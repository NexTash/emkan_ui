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

	onload: function (frm) {
		if (frm.doc.reference_doctype) {
			frappe.call({
				method: "emkan_ui.emkan_ui.doctype.custom_payment_request.custom_payment_request.get_print_format_list",
				args: { ref_doctype: frm.doc.reference_doctype },
				callback: function (r) {
					if (r.message && r.message.print_format) {
						set_field_options("print_format", r.message.print_format);
					}
				},
			});
		}
	},

	refresh: function (frm) {

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

		if (
			frm.doc.payment_request_type === "Outward" &&
			["Initiated", "Partially Paid"].includes(frm.doc.status) &&
			frm.doc.docstatus === 1
		) {
			frappe.db.get_list("Payment Entry", {
				filters: { reference_no: frm.doc.name },
				fields: ["name", "docstatus"]
			}).then(pes => {

				if (!pes || !pes.length) {
					frm.add_custom_button(__("Create Payment Entries"), function () {
						make_payment_entry(frm);
					}).addClass("btn-primary");
					return;
				}

				let total_paid = 0;

				let promises = pes.map(pe =>
					frappe.db.get_doc("Payment Entry", pe.name).then(doc => {
						if (doc.references && doc.references.length) {
							total_paid += doc.references.reduce(
								(sum, row) => sum + (row.allocated_amount || 0), 0
							);
						}
						return doc;
					})
				);

				Promise.all(promises).then(docs => {
					let request_amount = frm.doc.grand_total || 0;

					if (total_paid < request_amount) {
						frm.add_custom_button(__("Create Payment Entries"), function () {
							let matched_pe = docs.find(d => {
								let allocated = d.references.reduce(
									(sum, row) => sum + (row.allocated_amount || 0), 0
								);
								return allocated === request_amount;
							});

							if (matched_pe) {
								frappe.msgprint(__("A Payment Entry already exists."));
								frappe.set_route("Form", "Payment Entry", matched_pe.name);
							} else {
								make_payment_entry(frm);
							}
						}).addClass("btn-primary");
					}
				});
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
	},

	is_a_subscription: function (frm) {

		frm.toggle_reqd("payment_gateway_account", frm.doc.is_a_subscription);
		frm.toggle_reqd("subscription_plans", frm.doc.is_a_subscription);

		if (frm.doc.is_a_subscription && frm.doc.reference_doctype && frm.doc.reference_name) {
			frappe.call({
				method: "emkan_ui.emkan_ui.doctype.custom_payment_request.custom_payment_request.get_subscription_details",
				args: {
					reference_doctype: frm.doc.reference_doctype,
					reference_name: frm.doc.reference_name
				},
				freeze: true,
				callback: function (data) {
					if (!data.exc && data.message) {
						frm.clear_table("subscription_plans");

						(data.message || []).forEach(v => {
							let d = frappe.model.add_child(
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

			if (msg && msg.doctype && msg.name) {
				frm.set_value("reference_doctype", msg.doctype);
				frm.set_value("reference_name", msg.name);
				frm.save("Update");
			}

			if (Array.isArray(msg) && msg.length) {
				frappe.set_route("Form", msg[0].doctype, msg[0].name);
				frappe.msgprint(__("{0} Payment Entries created.", [msg.length]));
				return;
			}

			if (msg && msg.name) {
				frappe.set_route("Form", msg.doctype || "Payment Entry", msg.name);
				frappe.msgprint(__("Payment Entry {0} created.", [msg.name]));
				return;
			}

			frappe.msgprint(__("No Payment Entry created."));
		}
	});
}
