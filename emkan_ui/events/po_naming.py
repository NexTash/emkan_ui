
import frappe
import datetime
from frappe.model.naming import make_autoname


def autoname(doc, method=None):
    current_year = datetime.datetime.now().strftime("%y")
    digits = 6
    prefix = doc.custom_prefix
    current_number = int(make_autoname("test-", ignore_validate=True).split("-")[-1])
    formatted_number = format_with_leading_zeros(current_number, digits)
    doc.name = f"{prefix}{current_year}-{formatted_number}"

def format_with_leading_zeros(number, digits):
    return str(number).zfill(digits)