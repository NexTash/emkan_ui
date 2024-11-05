__version__ = "0.0.1"

from emkan_ui.override import custom_get_credit_and_debit_accounts
import erpnext.assets.doctype.asset.depreciation

erpnext.assets.doctype.asset.depreciation.get_credit_and_debit_accounts = custom_get_credit_and_debit_accounts