# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class DibsySettings(Document):
	def is_live(self):
		return self.environment == "Production"

	def get_base_url(self):
		url = (self.production_api_base_url if self.is_live() else self.test_api_base_url) or ""
		url = url.strip().rstrip("/")
		if not url:
			frappe.throw(_("Missing Dibsy API Base URL for the {0} environment.").format(self.environment))
		return url

	def get_secret_key(self):
		fieldname = "production_secret_key" if self.is_live() else "test_secret_key"
		key = (self.get_password(fieldname, raise_exception=False) or "").strip()
		if not key:
			frappe.throw(_("Missing Dibsy Secret Key for the {0} environment.").format(self.environment))
		return key

	def get_merchant_id(self):
		merchant_id = (self.production_merchant_id if self.is_live() else self.test_merchant_id) or ""
		return merchant_id.strip()

	def get_currency(self):
		return (self.default_currency or "QAR").strip() or "QAR"

	def get_organization(self):
		return (self.organization or "").strip()

	def get_organization_ar(self):
		return (self.organization_ar or "").strip()

	def get_organization_full_ar(self):
		return (self.organization_full_ar or "").strip()

	def get_license_number(self):
		return (self.license_number or "").strip()

	def get_event_type(self):
		return (self.event_type or "AFIFI_DONATION").strip() or "AFIFI_DONATION"

	def get_headers(self):
		return {
			"Authorization": f"Bearer {self.get_secret_key()}",
			"Content-Type": "application/json",
		}
