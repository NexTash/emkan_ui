frappe.listview_settings['Material Request'] = {
    onload: function(listview) {
        let interval = setInterval(() => {
            // ab sirf "dropdown-menu show" wali class ko target karo
            let $dropdown = $(listview.page.wrapper).find('.dropdown-menu.show');
            
            if ($dropdown.length) {
                if (!$dropdown.find('[data-view="MRList"]').length) {
                    $dropdown.append(`
                        <li data-view="MRList">
                            <a class="grey-link dropdown-item" href="#" onclick="frappe.set_route('query-report', 'MRList With Approval Date'); return false;">
                                <span class="menu-item-icon">
                                    <svg class="icon icon-sm" aria-hidden="true">
                                        <use href="#icon-small-file"></use>
                                    </svg>
                                </span>
                                <span class="menu-item-label" data-label="MRList%20With%20Approval%20Date">
                                    <span><span class="alt-underline">M</span>RList With Approval Date</span>
                                </span>
                            </a>
                        </li>
                    `);
                }

                clearInterval(interval);
            }
        }, 500);
    },
    add_fields: ["material_request_type", "status", "per_ordered", "per_received", "transfer_status"],
	get_indicator: function (doc) {
		var precision = frappe.defaults.get_default("float_precision");
		if (doc.status == "Stopped") {
			return [__("Stopped"), "red", "status,=,Stopped"];
		} else if (doc.transfer_status && doc.docstatus != 2) {
			if (doc.transfer_status == "Not Started") {
				return [__("Not Started"), "orange", "transfer_status,=,Not Started"];
			} else if (doc.transfer_status == "In Transit") {
				return [__("In Transit"), "yellow", "transfer_status,=,In Transit"];
			} else if (doc.transfer_status == "Completed") {
				if (doc.status == "Transferred") {
					return [__("Completed"), "green", "transfer_status,=,Completed"];
				} else {
					return [__("Partially Received"), "yellow", "per_ordered,<,100"];
				}
			}
		} else if (doc.docstatus == 1 && flt(doc.per_ordered, precision) == 0) {
			return [__("Pending"), "orange", "per_ordered,=,0|docstatus,=,1"];
		} else if (
			doc.docstatus == 1 &&
			flt(doc.per_ordered, precision) < 100 &&
			doc.material_request_type == "Material Transfer"
		) {
			return [__("Partially Received"), "yellow", "per_ordered,<,100"];
		} else if (doc.docstatus == 1 && flt(doc.per_ordered, precision) < 100) {
			return [__("Partially ordered"), "yellow", "per_ordered,<,100"];
		} else if (doc.docstatus == 1 && flt(doc.per_ordered, precision) == 100) {
			if (
				doc.material_request_type == "Purchase" &&
				flt(doc.per_received, precision) < 100 &&
				flt(doc.per_received, precision) > 0
			) {
				return [__("Partially Received"), "yellow", "per_received,<,100"];
			} else if (doc.material_request_type == "Purchase" && flt(doc.per_received, precision) == 100) {
				return [__("Received"), "green", "per_received,=,100"];
			} else if (["Purchase", "Manufacture"].includes(doc.material_request_type)) {
				return [__("Ordered"), "green", "per_ordered,=,100"];
			} else if (doc.material_request_type == "Material Transfer") {
				return [__("Transfered"), "green", "per_ordered,=,100"];
			} else if (doc.material_request_type == "Material Issue") {
				return [__("Issued"), "green", "per_ordered,=,100"];
			} else if (doc.material_request_type == "Customer Provided") {
				return [__("Received"), "green", "per_ordered,=,100"];
			}
		}
	},
};
