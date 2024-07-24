
import frappe
import datetime
from frappe.model.naming import make_autoname


# def autoname(doc, method=None):
#     current_year = datetime.datetime.now().strftime("%y")
#     digits = 6
#     prefix = doc.custom_prefix
#     current_number = int(make_autoname("test-", ignore_validate=True).split("-")[-1])
#     formatted_number = format_with_leading_zeros(current_number, digits)
#     doc.name = f"{prefix}{current_year}-{formatted_number}"

def autoname(doc, method=None):
    current_year = datetime.datetime.now().strftime("%y")
    digits = 6
    prefix = doc.custom_prefix

    # Fetch or create the settings document
    settings = frappe.get_single("PO Series counter")
    if not settings:
        settings = frappe.new_doc("PO Series counter")
        settings.lpo_series_counter = 125  # Initialize to one less than the starting number
        settings.save()

    # Increment the counter
    current_number = settings.lpo_series_counter + 1

    # Update the settings document
    settings.lpo_series_counter = current_number
    settings.save()

    # Format the new document name
    formatted_number = format_with_leading_zeros(current_number, digits)
    doc.name = f"{prefix}{current_year}-{formatted_number}"

def format_with_leading_zeros(number, digits):
    return str(number).zfill(digits)