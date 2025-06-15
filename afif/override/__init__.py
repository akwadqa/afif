from frappe import handler
from afif.override.handler import web_logout as custom_web_logout

handler.web_logout = custom_web_logout