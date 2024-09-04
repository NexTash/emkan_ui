frappe.ui.form.on("Purchase Receipt", {
    refresh(frm, dt, dn){
		if(frm.doc.docstatus < 1){
			frm.add_custom_button(
				__("Balance Quanity"),
				function () {
					if(frm.doc.items && frm.doc.items.length > 0){
						get_qty(frm, dt, dn)
					}
			},
		);
            frm.add_custom_button(
                __("Purchase Order"),
                function () {
                    if (!frm.doc.supplier) {
                        frappe.throw({
                            title: __("Mandatory"),
                            message: __("Please Select a Supplier"),
                        });
                    }
                    erpnext.utils.map_current_doc({
                        // method: "erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_receipt",
                        method: "emkan_ui.events.override.make_purchase_receipt",
                        source_doctype: "Purchase Order",
                        target: frm,
                        setters: {
                            supplier: frm.doc.supplier,
                            schedule_date: undefined,
                        },
                        get_query_filters: {
                            docstatus: 1,
                            status: ["not in", ["Closed", "On Hold"]],
                            per_received: ["<", 99.99],
                            company: frm.doc.company,
                        },
                        allow_child_item_selection: true,
                        child_fieldname: "items",
                        child_columns: ["item_code", "item_name", "qty"],
                    });
                },
                __("Get Items From")
            );
        }
    },
});

function get_qty(frm, dt, dn){
	for(let row of frm.doc.items){
		if(row.purchase_order){
			frappe.db.get_doc('Purchase Order', row.purchase_order)
			.then(doc => {
				for(let child of doc.items){
					if(child.item_code == row.item_code){
						frappe.model.set_value(row.doctype, row.name, "custom_order_qty", child.qty)
					}
				}
			})
		}
	}
}