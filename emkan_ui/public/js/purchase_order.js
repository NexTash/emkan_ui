frappe.ui.form.on("Purchase Order", {
    onload(frm, dt, dn){
		if(frm.doc.custom_department == "EMKAN-4 (BSI)"){
			frappe.model.set_value(dt, dn, "custom_prefix", "BSI-")
		}
		else{
			frappe.model.set_value(dt, dn, "custom_prefix", "EE-S-")
		}
    },
	custom_department(frm, dt, dn){
        if(frm.doc.custom_department == "EMKAN-4 (BSI)"){
            frappe.model.set_value(dt, dn, "custom_prefix", "BSI-")
        }
        else{
            frappe.model.set_value(dt, dn, "custom_prefix", "EE-S-")
        }
    },
    refresh(frm){
		frm.add_custom_button(
			__("Material Request"),
			function () {
				erpnext.utils.map_current_doc({
					method: "erpnext.stock.doctype.material_request.material_request.make_purchase_order",
					source_doctype: "Material Request",
					target: frm,
					setters: {
						schedule_date: undefined,
					},
					get_query_filters: {
						material_request_type: "Purchase",
						docstatus: 1,
						status: ["!=", "Stopped"],
						per_ordered: ["<", 100],
						company: frm.doc.company,
					},
					allow_child_item_selection: true,
					child_fieldname: "items",
					child_columns: ["item_code", "item_name", "qty", "ordered_qty"],
				});
			},
			__("Get Items From")
		);
    },
});