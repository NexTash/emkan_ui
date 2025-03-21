frappe.ui.form.on("Purchase Order Item", {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.item_code) {
            frappe.call({
                method: "frappe.db.sql",
                args: {
                    query: `SELECT MIN(rate) FROM \`tabPurchase Invoice Item\` WHERE item_code=%s`,
                    values: [row.item_code]
                },
                callback: function(response) {
                    if (response.message && response.message[0][0]) {
                        frappe.model.set_value(cdt, cdn, "custom_minimum_purchases_price", response.message[0][0]);
                    } else {
                        frappe.model.set_value(cdt, cdn, "custom_minimum_purchases_price", 0);
                    }
                }
            });
        }
    }
});
