// Copyright (c) 2024, NexTash and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk Scheduled Depreciation Posting tool", {
	asset_depreciation_schedule(frm) {
        if(frm.doc.asset_depreciation_schedule){
            frm.doc.depreciation_schedule = []
            frm.call("get_depreciations")
        }
        else{
            frm.doc.depreciation_schedule = []
            frm.refresh_field("depreciation_schedule")
        }
	},
    on_submit(frm){
        for(let row of frm.doc.depreciation_schedule){
            if (!row.journal_entry) {
                frappe.call({
                    method: "erpnext.assets.doctype.asset.depreciation.make_depreciation_entry",
                    args: {
                        asset_depr_schedule_name: frm.doc.asset_depreciation_schedule,
                        date: row.schedule_date,
                    },
                    callback: function (r) {
                        frappe.model.sync(r.message);
                        frm.refresh();
                    },
                });
            }
		}
    }
});
