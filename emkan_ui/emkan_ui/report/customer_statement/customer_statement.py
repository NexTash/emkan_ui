import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "date",
            "label": "Date",
            "fieldtype": "Date",
            "width": 120,
            "align": "left"
        },
        {
            "fieldname": "details",
            "label": "Reference",
            "fieldtype": "Data",
            "width": 200,
            "align": "left"
        },
        {
            "fieldname": "transactions",
            "label": "Tran Type",
            "fieldtype": "Data",
            "width": 150,
            "align": "left"
        },
        {
            "fieldname": "check_no",
            "label": "Check Ref / LPO",
            "fieldtype": "Data",
            "width": 150,
            "align": "left"
        },
        
        # {
        #     "fieldname": "currency",
        #     "label": "Currency",
        #     "fieldtype": "Data",
        #     "width": 120,
        #     "align": "left"
        # },
        # {
        #     "fieldname": "return_status",
        #     "label": "Remarks",
        #     "fieldtype": "Data",
        #     "width": 100,
        #     "align": "left"
        # },
        {
            "fieldname": "amount_dr",
            "label": "Debit",
            "fieldtype": "Data",
            "width": 120,
            "align": "right"
        },
        {
            "fieldname": "amount_cr",
            "label": "Credit",
            "fieldtype": "Data",
            "width": 120,
            "align": "right"
        },
        {
            "fieldname": "balance",
            "label": "Balance",
            "fieldtype": "Data",
            "width": 120,
            "align": "right"
        }
    ]

def get_opening_balance(filters):
    conditions = ""
    if filters.get("customer"):
        conditions += " AND party = %(customer)s"
    if filters.get("from_date"):
        conditions += " AND posting_date < %(from_date)s"

    opening_balance = frappe.db.sql(f"""
        SELECT
            SUM(debit) - SUM(credit) as opening_balance
        FROM
            `tabGL Entry`
        WHERE
            docstatus = 1
            AND party_type = 'Customer'
            {conditions}
    """, filters, as_dict=True)

    opening_balance_value = opening_balance[0].opening_balance if opening_balance else 0
    
    if opening_balance_value is None or opening_balance_value == 0 or opening_balance_value != opening_balance_value:
        return ""
    
    return opening_balance_value

def format_currency(value):
    if value is None:
        return ""
    return "{:,.2f}".format(value) if value else ""

def get_exchange_rate(from_currency, to_currency, date):
    exchange_rate = frappe.db.get_value("Currency Exchange", 
                                        {"from_currency": from_currency, "to_currency": to_currency, "date": ["<=", date]}, 
                                        "exchange_rate")
    if not exchange_rate:
        exchange_rate = frappe.db.get_value("Currency Exchange", 
                                            {"from_currency": from_currency, "to_currency": to_currency}, 
                                            "exchange_rate")
    return flt(exchange_rate) if exchange_rate else 1.0 

def convert_currency(amount, from_currency, to_currency, date):
    if from_currency == to_currency:
        return amount
    exchange_rate = get_exchange_rate(from_currency, to_currency, date)
    return amount / exchange_rate

def get_data(filters):
    default_currency = frappe.get_value("Company", filters.get("company"), "default_currency")
    opening_balance = get_opening_balance(filters)
    previous_balance = opening_balance

    balance = previous_balance 
    total_cr = 0
    total_dt = 0

    conditions = ""
    if filters.get("customer"):
        conditions += " AND party = %(customer)s"
    if filters.get("from_date"):
        conditions += " AND posting_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND posting_date <= %(to_date)s"
        
       
    gl_entries = frappe.db.sql(f"""
        SELECT
            posting_date,
            voucher_type,
            voucher_no,
            due_date,
            debit,
            credit,
            account_currency
        FROM
            `tabGL Entry`
        WHERE
            docstatus = 1
            AND party_type = 'Customer'
            {conditions}
        ORDER BY
            posting_date ASC, voucher_type ASC, voucher_no ASC
    """, filters, as_dict=True)

    data = []
    processed_references = set()

    data.append({
        "date": filters.get('from_date'),
        "transactions": "",
        "details": "",
        "check_no": "Opening Balance",
        # "return_status": "",
        "amount_dr": "",
        "amount_cr": "",
        "balance": format_currency(opening_balance)
    })

    if filters.get("customer"):
        cbc = frappe.db.get_value("Customer", filters.get("customer"), ["default_currency"]) 
    if not cbc:
        cbc = default_currency
    for entry in gl_entries:
        transactions = ""
        # return_status = ""
        details = ""
        check_no = ""
        amount_cr = entry['credit'] or 0
        amount_dr = entry['debit'] or 0

       
        if entry['account_currency'] and entry['account_currency'] != default_currency:
            amount_cr = convert_currency(amount_cr, entry['account_currency'], default_currency, entry['posting_date'])
            amount_dr = convert_currency(amount_dr, entry['account_currency'], default_currency, entry['posting_date'])

        if entry['voucher_no'] in processed_references:
            continue

        if entry['voucher_type'] == "Sales Invoice":
            status = frappe.db.get_value("Sales Invoice", ['docstatus'])
            if status == 2:
                continue
            
            if entry['voucher_type'] == "Sales Invoice":
                status, is_return = frappe.db.get_value("Sales Invoice", entry['voucher_no'], ['docstatus', 'is_return'])
                
                if status == 2:  # If the Sales Invoice is canceled, skip it
                    continue
                
                if is_return:
                    transactions = f"{entry['voucher_type']} (Credit MEMO)"
                else:
                    transactions = entry['voucher_type']
                
                details = f"{entry['voucher_no']}"
                        
        elif entry['voucher_type'] == "Payment Entry":
            pe_doc = frappe.get_doc("Payment Entry", entry['voucher_no'])
            if pe_doc.docstatus == 2:
                continue
            
            paid_amount = pe_doc.get('paid_amount', 0.0)
            # mode_of_payment = pe_doc.get('mode_of_payment', '')
            # cheque_no = pe_doc.get('cheque_no', pe_doc.get('reference_no', ''))

            # references = frappe.get_all("Payment Entry Reference", filters={"parent": entry['voucher_no']}, fields=["reference_name"])
            # reference_names = [ref['reference_name'] for ref in references]
            transactions = entry['voucher_type']
            check_no = pe_doc.reference_no or ""
            details = f"{entry['voucher_no']}"
            
            # if mode_of_payment:
            #     details += f", Mode of Payment: {mode_of_payment}"

            # if cheque_no:
            #     details += f", Cheque No./Reference: {cheque_no}"
            
            # if reference_names:
            #     details += f", {', '.join(reference_names)}"
            
            amount_cr = paid_amount

        elif entry['voucher_type'] == "Journal Entry":
            je_doc = frappe.get_doc("Journal Entry", entry['voucher_no'])
            if je_doc.docstatus == 2:
                continue
            
            # reference_number = je_doc.get('reference_number', '')
            # user_remark = je_doc.get('user_remark', '')
            transactions = entry['voucher_type']
            details = f"{entry['voucher_no']}"
            
            # if reference_number:
            #     details += f" Reference Number: {reference_number}"
            
            # if user_remark:
            #     if reference_number:
            #         details += f", User Remark: {user_remark}"
            #     else:
            #         details += f" User Remark: {user_remark}"

        total_cr += amount_cr
        total_dt += amount_dr
        balance = (previous_balance or 0) + (amount_dr - amount_cr)

        data.append({
            "date": entry['posting_date'],
            "transactions": transactions,
            "details": details,
            "check_no": check_no,
            "currency":cbc,
            # "return_status": return_status,
            "amount_dr": format_currency(amount_dr),
            "amount_cr": format_currency(amount_cr),
            "balance": format_currency(balance)
        })

        previous_balance = balance
        processed_references.add(entry['voucher_no'])

    data.append({
        "details": "",
        "check_no": "Total :",
        "amount_dr": format_currency(total_dt),
        "amount_cr": format_currency(total_cr),
        "balance": format_currency(balance)
    })

    return data