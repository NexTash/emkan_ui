# Copyright (c) 2024, NexTash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BulkScheduledDepreciationPostingtool(Document):
    def validate(self):
        asset_doc = frappe.get_doc('Asset Depreciation Schedule', self.asset_depreciation_schedule)
        # frappe.msgprint(f"{asset_doc}")
        for row in asset_doc.depreciation_schedule:
        	self.append("depreciation_schedule",{
					"schedule_date":row.schedule_date,
					"depreciation_amount":row.depreciation_amount,
					"accumulated_depreciation_amount":row.accumulated_depreciation_amount,
					"journal_entry":row.journal_entry
			})
            

