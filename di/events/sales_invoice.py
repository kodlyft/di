"""Sales Invoice event handlers for Digital Invoicing."""

import frappe
from frappe import _
from frappe.utils import cint

from di.constants import SRO_REQUIRED_SALE_TYPES


def before_submit(doc, method=None):
	"""Hook: before_submit on Sales Invoice."""
	from di.digital_invoicing.doctype.di_settings.di_settings import get_settings, is_enabled

	if not is_enabled(doc.company):
		return

	settings = get_settings(doc.company)
	if not settings:
		return

	if cint(doc.is_pos) and doc.pos_profile:
		profile = frappe.get_doc("POS Profile", doc.pos_profile)
		if cint(getattr(profile, "enable_fbr_integration", 0)):
			_validate_pos_items(doc)
			from di.integrations.pos_fiscal import fiscalize_invoice

			fiscalize_invoice(doc)
			_generate_qr(doc)
			return
		return

	if doc.customer and not cint(frappe.db.get_value("Customer", doc.customer, "enable_digital_invoicing")):
		return

	_validate_di_items(doc)

	if settings.auto_post_on_submit:
		from di.integrations.di_api import post_invoice

		post_invoice(doc)
		_generate_qr(doc)


def _validate_di_items(doc):
	"""Validate that items have required DI fields."""
	for item in doc.items:
		if not item.get("di_hs_code"):
			frappe.throw(
				_("Row {0}: HS Code is required for Digital Invoicing (Item: {1})").format(
					item.idx, item.item_name
				)
			)

		sale_type = item.get("di_sale_type") or ""
		if sale_type in SRO_REQUIRED_SALE_TYPES:
			if not item.get("di_sro_serial_no") and not item.get("di_schedule_no"):
				frappe.throw(
					_(
						"Row {0}: SRO Serial No or Schedule No is required for sale type '{1}' (Item: {2})"
					).format(item.idx, sale_type, item.item_name)
				)


def _validate_pos_items(doc):
	"""Validate POS items have required fields for FBR fiscal."""
	for item in doc.items:
		item_code = item.get("item_code")
		if not item_code:
			continue
		pct_code = frappe.db.get_value("Item", item_code, "customs_tariff_number")
		if not pct_code:
			frappe.throw(
				_(
					"Row {0}: Item {1} is missing Customs Tariff Number (PCT Code) required for FBR POS."
				).format(item.idx, item.item_name)
			)


def _generate_qr(doc):
	"""Generate QR code if invoice was posted successfully."""
	if doc.di_integration_id and not doc.di_qr_code:
		from di.integrations.qr_code import generate_qr_code

		doc.di_qr_code = generate_qr_code(doc.di_integration_id)
