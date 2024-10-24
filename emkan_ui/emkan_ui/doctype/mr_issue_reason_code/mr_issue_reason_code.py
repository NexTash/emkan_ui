# Copyright (c) 2024, nextash.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MRIssueReasonCode(Document):
	def validate(self):
		doc = frappe.get_doc("Report", "Emkan Accounts Payable")
		doc.db_set("add_total_row", 1)
		frappe.db.commit()
