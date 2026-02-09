from . import __version__ as app_version

app_name = "imprest_management"
app_title = "Imprest Management"
app_publisher = "Your Company"
app_description = "Complete imprest (cash advance) management system for Frappe/ERPNext"
app_email = "info@yourcompany.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/imprest_management/css/imprest_management.css"
# app_include_js = "/assets/imprest_management/js/imprest_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/imprest_management/css/imprest_management.css"
# web_include_js = "/assets/imprest_management/js/imprest_management.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "imprest_management/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "imprest_management.utils.jinja_methods",
#	"filters": "imprest_management.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "imprest_management.install.before_install"
after_install = "imprest_management.setup.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "imprest_management.uninstall.before_uninstall"
# after_uninstall = "imprest_management.uninstall.after_uninstall"

# Desk Notifications
# -------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "imprest_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"imprest_management.tasks.all"
#	],
#	"daily": [
#		"imprest_management.tasks.daily"
#	],
#	"hourly": [
#		"imprest_management.tasks.hourly"
#	],
#	"weekly": [
#		"imprest_management.tasks.weekly"
#	],
#	"monthly": [
#		"imprest_management.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "imprest_management.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "imprest_management.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "imprest_management.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]


# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"partial": 1,
#	},
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"imprest_management.auth.validate"
# ]

# Custom fields for existing doctypes
# ------------------------------------

# Custom fields that will be added to existing doctypes
fixtures = [
    "fixtures/workflow_state.json",
    "fixtures/workflow.json",
    {
        "dt": "Custom Field",
        "filters": [
            ["name", "in", [
                "Journal Entry-imprest_request"
            ]]
        ]
    }
]