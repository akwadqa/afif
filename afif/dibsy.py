# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

"""
Dibsy payment gateway integration for the donation flow.

NOTE: the exact endpoint paths, request/response field names, and webhook
signature scheme below have not been verified against Dibsy's official API
reference - they mirror a sibling in-house integration as a best-effort
baseline. Confirm the following against Dibsy's current docs / sandbox before
relying on this in production:
  - POST {base_url}/payments request/response shape
  - GET {base_url}/payments/{id} response shape and status values
  - the webhook signature header name and hashing algorithm
    (DIBSY_SIGNATURE_HEADER below is a placeholder)
"""

import hashlib
import hmac
import json

import frappe
from frappe import _
from frappe.integrations.utils import make_request
from frappe.utils import flt, get_url, now_datetime

DIBSY_SIGNATURE_HEADER = "Dibsy-Signature"

STATUS_MAP = {
	"paid": "Paid",
	"succeeded": "Paid",
	"completed": "Paid",
	"failed": "Failed",
	"declined": "Failed",
	"canceled": "Failed",
	"cancelled": "Failed",
	"expired": "Failed",
	"open": "Pending",
	"pending": "Pending",
	"authorized": "Pending",
}


def _settings():
	return frappe.get_single("Dibsy Settings")


def _post(path, payload):
	settings = _settings()
	return make_request(
		method="POST",
		url=f"{settings.get_base_url()}{path}",
		headers=settings.get_headers(),
		json=payload,
	)


def _get(path):
	settings = _settings()
	return make_request(
		method="GET",
		url=f"{settings.get_base_url()}{path}",
		headers=settings.get_headers(),
	)


def create_payment(donation):
	"""
	Create a Dibsy checkout payment for a Donation, store the gateway
	transaction id on it, and return the checkout URL the donor should be
	redirected to.
	"""
	settings = _settings()
	if not int(settings.is_enabled or 0):
		frappe.throw(_("Dibsy payment gateway is disabled. Enable it in Dibsy Settings."))

	amount = flt(donation.amount)
	currency = settings.get_currency()

	success_url = (settings.success_url or "").strip()
	if not success_url:
		frappe.throw(_("Missing Success Redirect URL in Dibsy Settings."))
	redirect_url = f"{success_url}?ref={donation.reference_id}"

	webhook_url = get_url("/api/method/afif.dibsy.dibsy_webhook")

	organization = settings.get_organization()
	program_title = frappe.db.get_value("Donation Program", donation.donation_program, "title") or donation.donation_program
	project_title = frappe.db.get_value("Donation Project", donation.donation_project, "title") or donation.donation_project

	payload = {
		"amount": {
			"value": f"{amount:.2f}",
			"currency": currency,
		},
		"description": f"{organization} - {program_title} - {project_title} - {donation.reference_id}",
		"redirectUrl": redirect_url,
		"webhookUrl": webhook_url,
		"metadata": {
			"paymentReference": donation.reference_id,
			"donation": donation.name,
			"organization": organization,
			"organizationAr": settings.get_organization_ar(),
			"organizationFull": settings.get_organization_full_ar(),
			"licenseNumber": settings.get_license_number(),
			"category": donation.donation_program,
			"categoryLabel": program_title,
			"project": donation.donation_project,
			"projectLabel": project_title,
			"donorName": donation.donor_name,
			"contactNumber": donation.donor_mobile,
			"email": donation.donor_email or "",
			"lang": frappe.local.lang or "ar",
			"eventType": settings.get_event_type(),
			"donationType": "online",
		},
	}

	try:
		res = _post("/payments", payload)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Dibsy create payment failed")
		frappe.throw(_("Unable to start payment with Dibsy. Please try again shortly."))

	payment_id = res.get("id")
	checkout_url = (((res.get("_links") or {}).get("checkout") or {}).get("href")) or ""

	if not payment_id or not checkout_url:
		frappe.log_error(
			message=json.dumps(res, indent=2, default=str),
			title="Dibsy create payment: missing id/checkout",
		)
		frappe.throw(_("Dibsy did not return a valid checkout link."))

	donation.db_set("gateway_transaction_id", payment_id, commit=True)

	return {"payment_url": checkout_url, "gateway_transaction_id": payment_id}


def fetch_payment(payment_id):
	return _get(f"/payments/{payment_id}")


def verify_webhook_signature(request):
	"""
	Verify the inbound webhook came from Dibsy via an HMAC-SHA256 over the raw
	request body, keyed by the Webhook Secret in Dibsy Settings. Fails closed
	(rejects) if no secret is configured or no signature header is present.
	"""
	secret = _settings().get_webhook_secret()
	if not secret:
		return False

	signature = request.headers.get(DIBSY_SIGNATURE_HEADER, "")
	if not signature:
		return False

	expected = hmac.new(secret.encode("utf-8"), request.get_data(), hashlib.sha256).hexdigest()
	return hmac.compare_digest(expected, signature)


def _apply_status(donation, dibsy_status, payment):
	if donation.payment_status == "Paid":
		# Already finalized - never re-credit or downgrade a completed donation.
		return

	mapped = STATUS_MAP.get((dibsy_status or "").lower(), "Pending")

	donation.payment_status = mapped
	donation.gateway_transaction_id = payment.get("id") or donation.gateway_transaction_id
	donation.payment_method = payment.get("method") or donation.payment_method

	if mapped == "Paid":
		donation.paid_at = now_datetime()
	elif mapped == "Failed":
		donation.failure_reason = payment.get("failureReason") or payment.get("status") or _("Payment failed")

	donation.save(ignore_permissions=True)
	frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def dibsy_webhook():
	"""
	Dibsy calls this when a payment's status changes. The webhook body is only
	used to identify which payment to look up - the actual status is re-fetched
	server-to-server from Dibsy before it is trusted and written onto the
	Donation, so a forged webhook body alone cannot mark a donation as paid.
	"""
	try:
		if not verify_webhook_signature(frappe.request):
			frappe.log_error("Dibsy webhook signature verification failed", "Dibsy Webhook")
			frappe.local.response.http_status_code = 401
			return "invalid signature"

		payload = frappe.request.get_json(silent=True) or {}
		payment_id = payload.get("id")
		if not payment_id:
			return "OK"

		payment = fetch_payment(payment_id)

		metadata = payment.get("metadata") or {}
		reference_id = metadata.get("reference_id")

		donation_name = None
		if reference_id:
			donation_name = frappe.db.get_value("Donation", {"reference_id": reference_id}, "name")
		if not donation_name:
			donation_name = frappe.db.get_value("Donation", {"gateway_transaction_id": payment_id}, "name")

		if not donation_name:
			frappe.log_error(
				title="Dibsy webhook: Donation not found",
				message=json.dumps(payment, indent=2, default=str),
				
			)
			return "OK"

		donation = frappe.get_doc("Donation", donation_name)
		_apply_status(donation, payment.get("status"), payment)

		return "OK"

	except Exception:
		frappe.log_error( "Dibsy webhook failed",frappe.get_traceback())
		return "OK"
