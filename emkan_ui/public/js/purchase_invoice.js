frappe.ui.form.on("Purchase Invoice", {
    refresh(frm, dt, dn){
		if(frm.doc.docstatus == 0){
            get_qty(frm, dt, dn);
            frm.add_custom_button(
				__("Purchase Receipt"),
				function () {
					erpnext.utils.map_current_doc({
						method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice",
						source_doctype: "Purchase Receipt",
						target: frm,
						setters: {
							supplier: frm.doc.supplier || undefined,
							posting_date: undefined,
						},
						get_query_filters: {
							docstatus: 1,
							status: ["not in", ["Closed", "Completed", "Return Issued"]],
							company: frm.doc.company,
							is_return: 0,
						},
						allow_child_item_selection: true,
						child_fieldname: "items",
						child_columns: ["item_code", "item_name", "qty", "amount",],
					});
				},
				__("Get Items From")
			);
        }
    },
});

frappe.ui.form.on("Purchase Invoice Item", {
    items_add: function(frm, cdt, cdn) {
        get_qty(frm, cdt, cdn);
    }
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