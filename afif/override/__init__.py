import frappe
from afif.override.handler import web_logout as custom_web_logout

frappe.handler.web_logout = custom_web_logout