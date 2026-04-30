
import frappe
import datetime

def autoname(doc, method=None):
    import datetime

    current_year = datetime.datetime.now().strftime("%y")
    digits = 6
    prefix = doc.custom_prefix

    settings = frappe.get_single("PO Series counter")

    if prefix == "EMK-ALM-":
        if settings.series_for_emkan_8 is None:
            frappe.throw("Please set counter in PO Series counter for EMKAN-8")

        current_counter = settings.series_for_emkan_8 + 1
        settings.series_for_emkan_8 = current_counter

    else:
        if settings.lpo_series_counter is None:
            frappe.throw("Please set counter in PO Series counter")

        current_counter = settings.lpo_series_counter + 1
        settings.lpo_series_counter = current_counter

    settings.save()

    formatted_number = format_with_leading_zeros(current_counter, digits)
    doc.name = f"{prefix}{current_year}-{formatted_number}"

def format_with_leading_zeros(number, digits):
    return str(number).zfill(digits)

def set_purchase_prices(doc, method):
    for item in doc.items:
        if not item.item_code or not item.item_name:
            continue

        past_purchases = frappe.get_all(
            "Purchase Order Item",
            filters={
                "item_code": item.item_code,
                "item_name": item.item_name,
                "docstatus": 1
            },
            fields=["rate", "uom", "parent", "creation"],
            order_by="creation desc",
            limit_page_length=100
        )

        if past_purchases:
            last_purchase = past_purchases[0]
            item.custom_last_pp = last_purchase["rate"]
            item.custom_last_uom = last_purchase["uom"]
            item.custom_last_po_doc = last_purchase["parent"]

            min_purchase = min(past_purchases, key=lambda x: x["rate"])
            item.custom_min_pp = min_purchase["rate"]
            item.custom_min_uom = min_purchase["uom"]
            item.custom_min_po_doc = min_purchase["parent"]
