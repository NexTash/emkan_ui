from datetime import datetime
import frappe
import json

from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate
from frappe.utils.background_jobs import enqueue
from datetime import datetime

from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
from erpnext.accounts.doctype.payment_entry.payment_entry import (
	get_company_defaults,
	get_payment_entry,
)
from erpnext.accounts.doctype.subscription_plan.subscription_plan import get_plan_rate
from erpnext.accounts.party import get_party_account, get_party_bank_account
from erpnext.accounts.utils import get_account_currency, get_currency_precision
from erpnext.utilities import payment_app_import_guard
 
@frappe.whitelist(allow_guest=True)
def make_payment_request1(**args):
	"""Make payment request"""

	args = frappe._dict(args)

	ref_doc = frappe.get_doc(args.dt, args.dn)
	gateway_account = get_gateway_details(args) or frappe._dict()

	grand_total = get_amount(ref_doc, gateway_account.get("payment_account"))
	if args.loyalty_points and args.dt == "Sales Order":
		from erpnext.accounts.doctype.loyalty_program.loyalty_program import validate_loyalty_points

		loyalty_amount = validate_loyalty_points(ref_doc, int(args.loyalty_points))
		frappe.db.set_value(
			"Sales Order", args.dn, "loyalty_points", int(args.loyalty_points), update_modified=False
		)
		frappe.db.set_value("Sales Order", args.dn, "loyalty_amount", loyalty_amount, update_modified=False)
		grand_total = grand_total - loyalty_amount

	bank_account = (
		get_party_bank_account(args.get("party_type"), args.get("party")) if args.get("party_type") else ""
	)

	draft_payment_request = frappe.db.get_value(
		"Payment Request",
		{"reference_doctype": args.dt, "reference_name": args.dn, "docstatus": 0},
	)

	existing_payment_request_amount = get_existing_payment_request_amount(args.dt, args.dn)

	if existing_payment_request_amount:
		grand_total -= existing_payment_request_amount

	if draft_payment_request:
		frappe.db.set_value(
			"Payment Request", draft_payment_request, "grand_total", grand_total, update_modified=False
		)
		pr = frappe.get_doc("Payment Request", draft_payment_request)
	else:
		pr = frappe.new_doc("Payment Request")

		if not args.get("payment_request_type"):
			args["payment_request_type"] = (
				"Outward" if args.get("dt") in ["Purchase Order", "Purchase Invoice"] else "Inward"
			)
		custom_department = frappe.db.get_value(args.get("dt"), args.get("dn"), "custom_department")
		pr.update(
			{
				"payment_gateway_account": gateway_account.get("name"),
				"payment_gateway": gateway_account.get("payment_gateway"),
				"payment_account": gateway_account.get("payment_account"),
				"payment_channel": gateway_account.get("payment_channel"),
				"payment_request_type": args.get("payment_request_type"),
				"currency": ref_doc.currency,
				"grand_total": grand_total,
				"mode_of_payment": args.mode_of_payment,
				"email_to": args.recipient_id or ref_doc.owner,
				"subject": _("Payment Request for {0}").format(args.dn),
				"message": gateway_account.get("message") or get_dummy_message(ref_doc),
				"reference_doctype": args.dt,
				"reference_name": args.dn,
				"company": ref_doc.get("company"),
				"party_type": args.get("party_type") or "Customer",
				"party": args.get("party") or ref_doc.get("customer"),
				"bank_account": bank_account,
				"custom_department" : custom_department
			}
		)

		# Update dimensions
		pr.update(
			{
				"cost_center": ref_doc.get("cost_center"),
				"project": ref_doc.get("project"),
			}
		)

		for dimension in get_accounting_dimensions():
			pr.update({dimension: ref_doc.get(dimension)})

		if args.order_type == "Shopping Cart" or args.mute_email:
			pr.flags.mute_email = True

		if frappe.db.get_single_value("Accounts Settings", "create_pr_in_draft_status", cache=True):
			pr.insert(ignore_permissions=True)
		if args.submit_doc:
			if pr.get("__unsaved"):
				pr.insert(ignore_permissions=True)
			pr.submit()

	if args.order_type == "Shopping Cart":
		frappe.db.commit()
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = pr.get_payment_url()

	if args.return_doc:
		return pr

	return pr.as_dict()

# def validate(self):
#         if self.party and self.party_type:
#             # Determine the name field based on party_type
#             if self.party_type == "Customer":
#                 name_field = "customer_name"
#             elif self.party_type == "Supplier":
#                 name_field = "supplier_name"
#             elif self.party_type == "Employee":
#                 name_field = "employee_name"
#             else:
#                 name_field = "name"  # Default field for any other party type
            
#             # Fetch the name field from the selected party document
#             party_doc_name = frappe.db.get_value(self.party_type, self.party, name_field)
#             self.custom_party_name = party_doc_name

def get_gateway_details(args):  # nosemgrep
	"""
	Return gateway and payment account of default payment gateway
	"""
	gateway_account = args.get("payment_gateway_account", {"is_default": 1})
	if gateway_account:
		return get_payment_gateway_account(gateway_account)

	gateway_account = get_payment_gateway_account({"is_default": 1})

	return gateway_account


def get_dummy_message(doc):
	return frappe.render_template(
		"""{% if doc.contact_person -%}
<p>Dear {{ doc.contact_person }},</p>
{%- else %}<p>Hello,</p>{% endif %}

<p>{{ _("Requesting payment against {0} {1} for amount {2}").format(doc.doctype,
	doc.name, doc.get_formatted("grand_total")) }}</p>

<a href="{{ payment_url }}">{{ _("Make Payment") }}</a>

<p>{{ _("If you have any questions, please get back to us.") }}</p>

<p>{{ _("Thank you for your business!") }}</p>
""",
		dict(doc=doc, payment_url="{{ payment_url }}"),
	)

def get_existing_payment_request_amount(ref_dt, ref_dn):
	"""
	Get the existing payment request which are unpaid or partially paid for payment channel other than Phone
	and get the summation of existing paid payment request for Phone payment channel.
	"""
	existing_payment_request_amount = frappe.db.sql(
		"""
		select sum(grand_total)
		from `tabPayment Request`
		where
			reference_doctype = %s
			and reference_name = %s
			and docstatus = 1
			and (status != 'Paid'
			or (payment_channel = 'Phone'
				and status = 'Paid'))
	""",
		(ref_dt, ref_dn),
	)
	return flt(existing_payment_request_amount[0][0]) if existing_payment_request_amount else 0


def get_payment_gateway_account(args):
	return frappe.db.get_value(
		"Payment Gateway Account",
		args,
		["name", "payment_gateway", "payment_account", "message"],
		as_dict=1,
	)

def get_amount(ref_doc, payment_account=None):
	"""get amount based on doctype"""
	dt = ref_doc.doctype
	if dt in ["Sales Order", "Purchase Order"]:
		grand_total = flt(ref_doc.rounded_total) or flt(ref_doc.grand_total)
	elif dt in ["Sales Invoice", "Purchase Invoice"]:
		if not ref_doc.get("is_pos"):
			if ref_doc.party_account_currency == ref_doc.currency:
				grand_total = flt(ref_doc.grand_total)
			else:
				grand_total = flt(ref_doc.base_grand_total) / ref_doc.conversion_rate
		elif dt == "Sales Invoice":
			for pay in ref_doc.payments:
				if pay.type == "Phone" and pay.account == payment_account:
					grand_total = pay.amount
					break
	elif dt == "POS Invoice":
		for pay in ref_doc.payments:
			if pay.type == "Phone" and pay.account == payment_account:
				grand_total = pay.amount
				break
	elif dt == "Fees":
		grand_total = ref_doc.outstanding_amount

	if grand_total > 0:
		return flt(grand_total, get_currency_precision())
	else:
		frappe.throw(_("Payment Entry is already created"))
  


def store_data(doc, method=None):
    # Get the current timestamp and date
    timestamp = frappe.utils.now()
    current_date = datetime.now().date()
    
    # Get the current workflow state and the previous state
    old_doc = doc.get_doc_before_save()
    user_doc = frappe.get_doc("User", frappe.session.user)
    
    # Proceed only if there is a change in workflow_state
    if old_doc and doc.workflow_state != old_doc.workflow_state:
        # Store the current workflow state in the custom field
        doc.custom_current_workflow_state = doc.workflow_state
        frappe.msgprint(f"{doc.custom_current_workflow_state}")
        
        # Check if the workflow state already exists in the child table
        state_exists = False
        for row in doc.custom_workflow_status:
            if row.workflow_states == doc.workflow_state:
                row.approved_by = frappe.session.user
                # Uncomment if additional fields are required
                row.approved_by_name = user_doc.full_name
                row.date = current_date
                state_exists = True
                break

        # Append the old workflow state only if it doesn't already exist
        if not state_exists:       
            doc.append("custom_workflow_status", {
                "workflow_states": old_doc.workflow_state,
                "approved_by": frappe.session.user,
                # Uncomment if additional fields are required
                "approved_by_name": user_doc.full_name,
                "date": current_date
            })


        # Remove any duplicate states if present
        old_states = []
        for row in doc.custom_workflow_status:
            if row.workflow_states != doc.workflow_state:
                old_states.append(row)
        doc.custom_workflow_status = []
        for state in old_states:
            doc.append("custom_workflow_status", state)
            
            
            
            
            
def last_state(doc, method=None):
    # Get the previous document
    old_doc = doc.get_doc_before_save()
    user_doc = frappe.get_doc("User", frappe.session.user)
    current_date = datetime.now().date()

    # Proceed only if there is a change in workflow_state
    if old_doc and doc.workflow_state != old_doc.workflow_state:
        # Set the custom current workflow state
        doc.custom_current_workflow_state = doc.workflow_state

        # Append COO Approved status to the child table
        doc.append("custom_workflow_status", {
            "workflow_states": "Acc Manager Approval",
            "approved_by": frappe.session.user,
            "approved_by_name" : user_doc.full_name,
            "date" : current_date
        })