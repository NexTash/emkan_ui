import frappe

def set_child_asset(doc, method=None):
    for row in doc.depreciation_schedule:
        row.custom_asset = doc.asset