from urllib.parse import parse_qs, urlparse

import frappe
from frappe.auth import CookieManager, LoginManager
from frappe.tests import IntegrationTestCase
from frappe.utils import random_string, set_request

from afif.hooks_call import update_password

NEW_PASSWORD = "Afif-Strong-Pass-2026!"


class TestUpdatePasswordRedirect(IntegrationTestCase):
    def setUp(self):
        set_request(path="/update-password")
        frappe.local.cookie_manager = CookieManager()
        frappe.local.login_manager = LoginManager()
        self.user = frappe.get_doc(
            {
                "doctype": "User",
                "email": f"signup-{random_string(8)}@example.com",
                "first_name": "Signup",
                "user_type": "Website User",
                "send_welcome_email": 0,
            }
        ).insert(ignore_permissions=True)
        self.key = parse_qs(urlparse(self.user._reset_password()).query)["key"][0]

    def tearDown(self):
        frappe.set_user("Administrator")

    def test_website_user_returns_to_the_page_they_signed_up_from(self):
        # sign_up caches the page the user came from, e.g. the scholarship page.
        frappe.cache.hset("redirect_after_login", self.user.name, "/scholarship")

        self.assertEqual(update_password(NEW_PASSWORD, key=self.key), "/scholarship")

    def test_website_user_without_a_signup_page_goes_to_the_profile(self):
        self.assertEqual(update_password(NEW_PASSWORD, key=self.key), "beneficiary-profile")
