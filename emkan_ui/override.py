import frappe


def custom_get_credit_and_debit_accounts(accumulated_depreciation_account, depreciation_expense_account):
	root_type = frappe.get_value("Account", depreciation_expense_account, "root_type")

	if root_type == "Expense":
		credit_account = accumulated_depreciation_account
		debit_account = depreciation_expense_account
	elif root_type == "Income":
		credit_account = depreciation_expense_account
		debit_account = accumulated_depreciation_account
	else:
		credit_account = accumulated_depreciation_account
		debit_account = depreciation_expense_account
		# frappe.throw(_("Depreciation Expense Account should be an Income or Expense Account."))

	return credit_account, debit_account