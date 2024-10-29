# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from emkan_ui.emkan_ui.report.emkan_receivable_summary.emkan_receivable_summary import (
	AccountsReceivableSummary,
)


def execute(filters=None):
	args = {
		"account_type": "Payable",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return AccountsReceivableSummary(filters).run(args)
