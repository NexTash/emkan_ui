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

@frappe.whitelist()
def get_purchase_prices(item_code):
    if not item_code:
        return {"min_price": 0}

    # Get all purchase invoice items for this item
    purchase_items = frappe.db.get_all("Purchase Invoice Item",
        filters={"item_code": item_code},
        fields=["rate"]
    )

    if not purchase_items:
        return {"min_price": 0}

    # Get minimum price
    min_price = min(item.rate for item in purchase_items) if purchase_items else 0

    return {"min_price": min_price}
