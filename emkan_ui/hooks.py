app_name = "emkan_ui"
app_title = "Emkan Ui"
app_publisher = "NexTash"
app_description = "emkan_ui"
app_email = "support@emkan_ui.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/emkan_ui/css/emkan_ui.css"
# app_include_js = "/assets/emkan_ui/js/emkan_ui.js"

# include js, css files in header of web template
# web_include_css = "/assets/emkan_ui/css/emkan_ui.css"
# web_include_js = "/assets/emkan_ui/js/emkan_ui.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "emkan_ui/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Stock Entry" : "public/js/stock_entry.js",
              "Payment Entry" : "public/js/payment_entry.js",
              "Purchase Order" : "public/js/purchase_order.js"
              }
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "emkan_ui/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "emkan_ui.utils.jinja_methods",
# 	"filters": "emkan_ui.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "emkan_ui.install.before_install"
# after_install = "emkan_ui.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "emkan_ui.uninstall.before_uninstall"
# after_uninstall = "emkan_ui.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "emkan_ui.utils.before_app_install"
# after_app_install = "emkan_ui.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "emkan_ui.utils.before_app_uninstall"
# after_app_uninstall = "emkan_ui.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "emkan_ui.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Purchase Order": {
		"autoname": "emkan_ui.events.po_naming.autoname",
	},
    "DocShare": {
        "after_insert": "emkan_ui.events.share_emkan.after_insert",
    },
    "ToDo":{
        "on_update": "emkan_ui.events.share_emkan.remove_share"
    },
    "Expense Claim":{
        "validate": "emkan_ui.events.expense_claim.get_account_user"
	},
    # "Material Request": {
	# 	"on_update": [
    #             # "emkan_ui.events.material_request.change_state",
    #             "emkan_ui.events.material_request.assign_user"
    #             ]
	# }
    
      "Material Request": {
		"on_update": [
                "emkan_ui.events.material_request.change_state",
                "emkan_ui.events.material_request.assign_user",
                ],
        "before_save": ["emkan_ui.events.workflow.store_data"],
        "before_submit": ["emkan_ui.events.workflow.last_state"],
        
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"emkan_ui.tasks.all"
	# ],
	# "daily": [
	# 	"emkan_ui.tasks.daily"
	# ],
	"hourly": [
		"emkan_ui.events.material_request.change_state"
	],
	# "weekly": [
	# 	"emkan_ui.tasks.weekly"
	# ],
	# "monthly": [
	# 	"emkan_ui.tasks.monthly"
	# ],
}

# Testing
# -------

# before_tests = "emkan_ui.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "emkan_ui.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "emkan_ui.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["emkan_ui.utils.before_request"]
# after_request = ["emkan_ui.utils.after_request"]

# Job Events
# ----------
# before_job = ["emkan_ui.utils.before_job"]
# after_job = ["emkan_ui.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"emkan_ui.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
fixtures=[
    {
        "dt" : "Workflow State",
        "filters": [
            [
                "name","in",
                [
                    "Draft",
                    "Submit for Approval",
                    "Approval reqd by Account Lead",
                    "Approval reqd by Finance Director",
                    "Approval reqd by Account User",
                    "Approved by Finance Director",
                    "Completed",
                    "Rejected",
                    "Verified by Senior Accountant",
                    "Approved by Lead Accountant",
                    "Recommended by Finance Director",
                    "MR Prepared",
                    "Store Verification",
                    "Pending Mgmt. Approval",
                    "Mgmt Approved",
                    "Move to Purchase",
                    "Verified by Account User",
                    "Recommended by Lead Account",
                    "Approved by Senior Accountant",
                    "Submit",
                    "Approved by EXE Manager",
                    "Submitted",
                    "MR Prepared",
                    "Store Verification",
                    "Dept. Verification",
                    "Dept. Review",
                    "Pending Head Of Service Approval",
                    "CAPEX Verification",
                    "CAPEX Review",
                    "Pending COO Approval",
                    "COO Approval",
                    "COO Approved",
                    "Pending Mgmt. Approval",
                    "Mgmt Approved",
                    "Prepared",
                    "Approval Reqd by Manager",
                    "PO issued",
                    "Approval Reqd by Manager",
                ]
            ]
        ]
    },
    {
        "dt" : "Role",
        "filters": [
            [
                "name","in",
                [
                    "No",
                    "Yes",
                    "Account user",
                    "Account Lead",
                    "Finance Director",
                    "Senior Accountant",
                    "Lead Accountant",
                    "MR Creator",
                    "Store Verifier",
                    "MR Approver",
                    "EXE APPROVER",
                    "Store Verifier",
                    "MR Verifier",
                    "MR Reviewer",
                    "CAPEX Reviewer",
                    "COO",
                    "MR Approver",
                    "Purchase User",
                    "Purchase Manager",
                    "All"
                ]
            ]
        ]
    },
    {
        "dt" : "Workflow Action Master",
        "filters": [
            [
                "name","in",
                [
                    "Return for Update",
                    "Submit",
                    "Submit for Approval",
                    "Return to Initiator",
                    "Approve",
                    "Return to Senior Accountant",
                    "Reject",
                    "Return to Lead Accountant",
                    "Send For Store Verification",
                    "Send For Mgmt. Approval",
                    "Return Back To Initiator",
                    "Return to Account User",
                    "Send For CAPEX Verify",
                    "Return to Verifier",
                    "Return to Reviewer"
                ]
            ]
        ]
    },
    {
        "dt" : "Workflow",
        "filters": [
            [
                "name","in",
                [
                    "Purchase Order",
                    "Payment Request",
                    "MR-Approval-Flow",
                    "Expense Claim",
                    "Employee Advance",
                    "MR-Approval-Flow-V4",
                ]
            ]
        ]
    },
    {
        "dt" : "Payment Type",
        "filters": [
            [
                "name","in",
                [
                    "Pantry & Refreshment Expenses",
                    "Electricity & Water Charges",
                    "Communication Expenses",
                    "Penaly & other Fine Charges",
                    "Vehicle Maintenance",
                    "Mess Expenses",
                    "Visa & Imigration Expenses",
                    "Employee Welfare Expenses",
                    "Office & Admin Expenses",
                    "Fuel Expenses",
                    "Employee Advance",
                    "Administration Related expenses",
                    "Management expenses",
                ]
            ]
        ]
    },
    # {
    #     "dt" : "Letter Head",
    #     "filters": [
    #         [
    #             "name","in",
    #             [
    #                 "Emkan",
    #                 "Emkan Ui"
    #             ]
    #         ]
    #     ]
    # }
]







