# Copyright (c) 2024, NexTash and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from frappe.model.document import Document

class BulkScheduledDepreciationPostingtool(Document):
	@frappe.whitelist()
	def get_depreciations(self):
		today = datetime.now().date()
		asset_doc = frappe.get_doc('Asset Depreciation Schedule', self.asset_depreciation_schedule)
		for row in asset_doc.depreciation_schedule:
			if row.schedule_date < today:
				self.append("depreciation_schedule",{
					"schedule_date":row.schedule_date,
					"depreciation_amount":row.depreciation_amount,
					"accumulated_depreciation_amount":row.accumulated_depreciation_amount,
					# "journal_entry":row.journal_entry
				})
            

