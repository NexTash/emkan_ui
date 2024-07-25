
import frappe
import datetime

def autoname(doc, method=None):
    current_year = datetime.datetime.now().strftime("%y")
    digits = 6
    prefix = doc.custom_prefix

    settings = frappe.get_single("PO Series counter")
    if not settings.lpo_series_counter:
        frappe.throw("Please set counter in PO Series counter")

    current_number = settings.lpo_series_counter + 1

    settings.lpo_series_counter = current_number
    settings.save()

    formatted_number = format_with_leading_zeros(current_number, digits)
    doc.name = f"{prefix}{current_year}-{formatted_number}"

def format_with_leading_zeros(number, digits):
    return str(number).zfill(digits)