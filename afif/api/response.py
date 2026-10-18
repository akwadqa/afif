from typing import Any

import frappe


def gen_response(status_code: int, message: str, data: Any = None) -> None:
    frappe.response["http_status_code"] = status_code
    frappe.response["message"] = message
    frappe.response["data"] = data
