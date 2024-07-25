frappe.ui.form.on("Purchase Order", {
    custom_department(frm, dt, dn){
        if(frm.doc.custom_department == "BSI"){
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
	// validate: function(frm) {
    //     // Check if there are any items in the Purchase Order
    //     if (frm.doc.items && frm.doc.items.length > 0) {
    //         let has_mr = false;
    //         // Loop through the items to check if any of them has a linked Material Request
    //         frm.doc.items.forEach(function(item) {
    //             if (item.material_request) {
    //                 has_mr = true;
    //             }
    //         });

    //         if (!has_mr) {
    //             // Throw an error if no Material Request is linked
    //             frappe.msgprint(__('You cannot create a Purchase Order without a linked Material Request.'));
    //             frappe.validated = false;
    //         }
    //     }
    // }

});