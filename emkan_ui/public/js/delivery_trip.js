frappe.ui.form.on('Delivery Trip', {
    onload: function(frm) {
        if (frm.is_new() && !frm.doc.custom_date) {
            frm.set_value('custom_date', frappe.datetime.get_today());
        }

        frm.set_df_property('custom_model', 'hidden', false);
        frm.set_df_property('custom_model', 'read_only', true);
        frm.toggle_display('custom_model', true);

        if (frm.doc.vehicle) {
            fetch_and_set_model(frm);
        }
    },

    refresh: function(frm) {
        frm.set_df_property('custom_model', 'hidden', false);
        frm.set_df_property('custom_model', 'read_only', true);
        frm.toggle_display('custom_model', true);
    },

    vehicle: function(frm) {
        if (!frm.doc.vehicle) {
            frm.set_value('custom_model', null);
            return;
        }
        fetch_and_set_model(frm);
    },

    custom_end_time: function(frm) {
        if (frm.doc.custom_end_time && frm.doc.departure_time) {
            if (frm.doc.custom_end_time <= frm.doc.departure_time) {
                frappe.msgprint("End Time must be strictly greater than Departure Time.");
                frm.set_value('custom_end_time', null);
            }
        }
    },

    custom_km: function(frm) {
        if (!frm.doc.vehicle || !frm.doc.custom_km) {
            return;
        }

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Delivery Trip",
                filters: { vehicle: frm.doc.vehicle },
                order_by: "custom_date desc, name desc",
                limit_page_length: 1,
                fields: ["custom_km"]
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    let last_km = parseFloat(r.message[0].custom_km || 0);
                    let current_km = parseFloat(frm.doc.custom_km || 0);

                    if (current_km <= last_km) {
                        frappe.msgprint({
                            title: __('Invalid KM Entry'),
                            indicator: 'red',
                            message: `KM must be greater than last trip KM (${last_km}).`
                        });
                        frm.set_value('custom_km', null);
                    }
                }
            }
        });
    },

    validate: function(frm) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Delivery Trip",
                filters: [
                    ["name", "!=", frm.doc.name],
                    ["custom_date", "=", frm.doc.custom_date],
                    ["departure_time", "=", frm.doc.departure_time]
                ],
                fields: ["name", "custom_date", "departure_time"],
                limit_page_length: 1
            },
            async: false,
            callback: function(r) {
                if (r.message?.length) {
                    frm.set_value('custom_date', null);
                    frm.set_value('departure_time', null);
                    frappe.throw(`A booking already exists on ${frappe.format(frm.doc.custom_date, {fieldtype:'Date'})} at ${frm.doc.departure_time}.`);
                }
            }
        });

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Delivery Trip",
                filters: [
                    ["name", "!=", frm.doc.name],
                    ["custom_date", "=", frm.doc.custom_date]
                ],
                fields: ["name"],
                limit_page_length: 1
            },
            async: false,
            callback: function(r) {
                if (r.message?.length) {
                    frm.set_value('custom_date', null);
                    frappe.throw(`A booking already exists on ${frappe.format(frm.doc.custom_date, {fieldtype:'Date'})}.`);
                }
            }
        });

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Delivery Trip",
                filters: [
                    ["name", "!=", frm.doc.name],
                    ["departure_time", "=", frm.doc.departure_time]
                ],
                fields: ["name"],
                limit_page_length: 1
            },
            async: false,
            callback: function(r) {
                if (r.message?.length) {
                    frm.set_value('departure_time', null);
                    frappe.throw(`A booking already exists at ${frm.doc.departure_time}.`);
                }
            }
        });
    }
});

function fetch_and_set_model(frm) {
    frappe.db.get_value('Vehicle', frm.doc.vehicle, 'model')
        .then(r => {
            let model_value = (r && r.message) ? (r.message.model || r.message['model'] || null) : null;
            frm.set_value('custom_model', model_value);
        })
        .catch(() => {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Vehicle",
                    fieldname: "model",
                    filters: { name: frm.doc.vehicle }
                },
                callback: function(res) {
                    if (res && res.message) {
                        frm.set_value('custom_model', res.message.model);
                    } else {
                        frm.set_value('custom_model', null);
                    }
                }
            });
        });
}