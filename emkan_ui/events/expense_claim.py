import frappe
import datetime

def get_account_user(doc, method=None):
    if doc.workflow_state == "Verified by Account User":
        # doc.reload()
        # frappe.db.set_value(doc.doctype, doc.name, "custom_account_user", frappe.session.user)
        doc.db_set("custom_account_user", frappe.session.user)
        # doc.db_update()
    # frappe.db.commit()