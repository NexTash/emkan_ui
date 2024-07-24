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
doctype_js = {
    "Stock Entry" : "public/js/stock_entry.js",
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
		"validate": "emkan_ui.events.po_naming.autoname",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"emkan_ui.tasks.all"
# 	],
# 	"daily": [
# 		"emkan_ui.tasks.daily"
# 	],
# 	"hourly": [
# 		"emkan_ui.tasks.hourly"
# 	],
# 	"weekly": [
# 		"emkan_ui.tasks.weekly"
# 	],
# 	"monthly": [
# 		"emkan_ui.tasks.monthly"
# 	],
# }

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
<<<<<<< HEAD

# fixtures=[]
=======
fixtures=[
    {
        "dt" : "Workflow State",
        "filters": [
            [
                "name","in",
                [
                    "Approval 1",
                    "Approval 2",
                    "Approval 3",
                    "Approval 4",
                    "Approval 5",    
                    "Approval 6",
                    "Approval 7",
                    "Approval 8",
                    "Draft",
                    "Submit for Approval",
                    "Approval reqd by Account Lead",
                    "Approval reqd by Finance Director",
                    "Approval reqd by Account User",
                    "Approved by Finance Director",
                    "Completed",
                    "Rejected",
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
                    "Role 1",
                    "Role 2",
                    "Role 3",    
                    "Role 4",
                    "Role 5",
                    "Role 6",
                    "Role 7",
                    "Role 8",
                    "Account user",
                    "Account Lead",
                    "Finance Director",
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
                    "submit",
                    "Submit for Approval",
                    
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
>>>>>>> develop







