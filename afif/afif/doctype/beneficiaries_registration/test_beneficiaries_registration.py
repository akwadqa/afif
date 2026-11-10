# Copyright (c) 2025, Akwad and Contributors
# See license.txt

import frappe
import frappe.client
from frappe.tests import IntegrationTestCase

from afif.afif.doctype.beneficiaries_registration.beneficiaries_registration import AccountRestrictionScopeError
from afif.api.test_scholarship import make_beneficiary_user, make_pdf, make_registration


class TestReplacedAttachmentCleanup(IntegrationTestCase):
    def setUp(self):
        self.addCleanup(frappe.set_user, "Administrator")
        frappe.set_user(make_beneficiary_user())
        self.registration = make_registration(is_scholarship=1)

    def test_replacing_an_attachment_deletes_the_old_file(self):
        old_file = self.attach("qid")

        new_file = self.attach("qid")

        self.assertFalse(frappe.db.exists("File", old_file.name))
        self.assertFalse(old_file.exists_on_disk())
        self.assertTrue(frappe.db.exists("File", new_file.name))
        self.assertTrue(new_file.exists_on_disk())

    def test_clearing_an_attachment_deletes_its_file(self):
        file = self.attach("passport")

        self.set_field("passport", None)

        self.assertFalse(frappe.db.exists("File", file.name))

    def test_same_upload_on_another_field_is_kept(self):
        content = make_pdf()
        first = self.attach("wife_id", content)
        second = self.attach("wife_passport", content)
        # Frappe stores identical uploads once and shares the file_url.
        self.assertEqual(first.file_url, second.file_url)

        self.set_field("wife_id", None)

        self.assertFalse(frappe.db.exists("File", first.name))
        self.assertTrue(frappe.db.exists("File", second.name))
        self.assertTrue(second.exists_on_disk())

    def test_saving_without_changes_keeps_the_files(self):
        file = self.attach("iban_picture")

        registration = frappe.get_doc("Beneficiaries Registration", self.registration)
        registration.en_name = "Unchanged Attachments"
        registration.save()

        self.assertTrue(frappe.db.exists("File", file.name))

    def attach(self, fieldname: str, content: bytes | None = None):
        """Upload a private file to the registration field and save it, like the wizard does."""
        file = frappe.get_doc(
            {
                "doctype": "File",
                "file_name": f"{fieldname}.pdf",
                "content": content or make_pdf(),
                "is_private": 1,
                "attached_to_doctype": "Beneficiaries Registration",
                "attached_to_name": self.registration,
                "attached_to_field": fieldname,
            }
        ).insert()
        self.set_field(fieldname, file.file_url)
        return file

    def set_field(self, fieldname: str, value: str | None) -> None:
        registration = frappe.get_doc("Beneficiaries Registration", self.registration)
        registration.set(fieldname, value)
        registration.save()


class TestAccountRestrictionScope(IntegrationTestCase):
    def setUp(self):
        self.addCleanup(frappe.set_user, "Administrator")
        frappe.set_user(make_beneficiary_user())

    def restrict(self, registration: str) -> None:
        frappe.set_user("Administrator")
        registration_doc = frappe.get_doc("Beneficiaries Registration", registration)
        registration_doc.is_account_restricted = 1
        registration_doc.save()

    def test_normal_registration_cannot_be_restricted(self):
        registration = make_registration(is_scholarship=0)

        with self.assertRaises(AccountRestrictionScopeError):
            self.restrict(registration)

        self.assertEqual(frappe.db.get_value("Beneficiaries Registration", registration, "is_account_restricted"), 0)

    def test_scholarship_registration_can_be_restricted(self):
        registration = make_registration(is_scholarship=1)

        self.restrict(registration)

        self.assertEqual(frappe.db.get_value("Beneficiaries Registration", registration, "is_account_restricted"), 1)


class TestScholarshipFlagOmittedOnSave(IntegrationTestCase):
    """A portal opened before the scholarship release saves the whole registration without the flag."""

    def setUp(self):
        self.addCleanup(frappe.set_user, "Administrator")
        frappe.set_user(make_beneficiary_user())

    def test_normal_registration_saves_without_the_flag(self):
        registration = make_registration(is_scholarship=0)

        save_without_scholarship_flag(registration)

        self.assertEqual(frappe.db.get_value("Beneficiaries Registration", registration, "is_scholarship"), 0)

    def test_scholarship_registration_keeps_the_flag(self):
        registration = make_registration(is_scholarship=1)

        save_without_scholarship_flag(registration)

        self.assertEqual(frappe.db.get_value("Beneficiaries Registration", registration, "is_scholarship"), 1)


def save_without_scholarship_flag(registration: str) -> None:
    payload = frappe.get_doc("Beneficiaries Registration", registration).as_dict()
    del payload["is_scholarship"]
    frappe.client.save(frappe.as_json(payload))


class TestAttachmentsTabLayout(IntegrationTestCase):
    def test_site_field_order_keeps_the_documents_on_the_attachments_tab(self):
        # The site's Customize Form field_order wins over the JSON, so a tab added after a field
        # it moved can pull the remaining documents into that tab.
        standard_fields = frappe.get_doc("DocType", "Beneficiaries Registration").fields
        effective_fields = frappe.get_meta("Beneficiaries Registration").fields

        documents = get_tab_fields(standard_fields, "attachment_tab")

        self.assertIn("additional_documents", documents)
        self.assertEqual(get_tab_fields(effective_fields, "attachment_tab"), documents)


def get_tab_fields(fields, tab_fieldname: str) -> set[str]:
    tab = None
    tab_fields = set()
    for df in fields:
        if df.fieldtype == "Tab Break":
            tab = df.fieldname
        elif tab == tab_fieldname:
            tab_fields.add(df.fieldname)
    return tab_fields
