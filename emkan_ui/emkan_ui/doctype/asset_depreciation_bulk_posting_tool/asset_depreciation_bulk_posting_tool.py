# Copyright (c) 2024, NexTash and contributors
# For license information, please see license.txt

import frappe
from erpnext.assets.doctype.asset.depreciation import make_depreciation_entry
from frappe.model.document import Document


class AssetDepreciationBulkPostingTool(Document):
	def before_save(self):
		if self.from_date and self.to_date:
			self.depreciation_schedule = []
			self.get_depreciations()
	
	def before_submit(self):
		for row in self.depreciation_schedule:
			dep_doc = make_depreciation_entry(row.asset_depreciation_schedule, row.schedule_date)
			journal_entry = "abc"
			for child in dep_doc.depreciation_schedule:
				if row.accumulated_depreciation_amount == child.accumulated_depreciation_amount:
					journal_entry = child.journal_entry
					break
			row.journal_entry = journal_entry
	def get_depreciations(self):
		# SQL query to get depreciation schedule with date range filter and non-empty journal entry
		depreciation_schedules = frappe.db.sql("""
			SELECT 
				ads.asset,  -- Adding asset field to the select
				ads.name AS asset_depreciation_schedule,  -- Name of the asset depreciation schedule
				ds.schedule_date, 
				ds.depreciation_amount, 
				ds.accumulated_depreciation_amount, 
				ds.journal_entry
			FROM 
				`tabDepreciation Schedule` ds
			INNER JOIN 
				`tabAsset Depreciation Schedule` ads ON ds.parent = ads.name
			INNER JOIN 
				`tabAsset` fa ON ads.asset = fa.name
			WHERE 
				ds.schedule_date BETWEEN %s AND %s
				AND (ds.journal_entry IS NULL OR ds.journal_entry = '')
				AND ads.docstatus = 1  -- Ensure asset depreciation schedule is submitted
			ORDER BY 
            	ds.schedule_date ASC  -- Sort results by schedule_date in ascending order
		""", (self.from_date, self.to_date), as_dict=True)
		# Append each row to the 'depreciation_schedule' table
		for row in depreciation_schedules:
			# frappe.msgprint(f"{row}")
			self.append("depreciation_schedule", {
				"asset": row['asset'],  # Asset field from the asset depreciation schedule
				"asset_depreciation_schedule": row['asset_depreciation_schedule'],  # The name of the asset depreciation schedule
				"schedule_date": row['schedule_date'],  # Schedule date
				"depreciation_amount": row['depreciation_amount'],  # Depreciation amount
				"accumulated_depreciation_amount": row['accumulated_depreciation_amount'],  # Accumulated depreciation amount
				"journal_entry": row['journal_entry']  # Journal entry
			})
