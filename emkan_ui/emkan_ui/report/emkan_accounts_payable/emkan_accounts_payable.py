# Copyright (c) 2024, NexTash and contributors
# For license information, please see license.txt

from emkan_ui.emkan_ui.report.emkan_accounts_receivable.emkan_accounts_receivable import ReceivablePayableReport


def execute(filters=None):
	args = {
		"account_type": "Payable",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return ReceivablePayableReport(filters).run(args)
