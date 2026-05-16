"""FBR POS Fiscal integration.

Handles POS invoice fiscalization via FBR's POS Integration Services API.
"""
import json
import re
from dataclasses import dataclass

import frappe
import requests
from frappe import _
from frappe.utils import cint, cstr, flt, now_datetime

from di.constants import (
	PAYMENT_MODE_CARD,
	PAYMENT_MODE_CASH,
	PAYMENT_MODE_CHEQUE,
	PAYMENT_MODE_GIFT_VOUCHER,
	PAYMENT_MODE_LOYALTY,
	PAYMENT_MODE_MIXED,
	POS_INVOICE_3RD_SCHEDULE_CREDIT,
	POS_INVOICE_3RD_SCHEDULE_NEW,
	POS_INVOICE_CREDIT,
	POS_INVOICE_NEW,
	POS_PROD_URL,
	POS_SANDBOX_URL,
	POS_SUCCESS_CODES,
)
from di.digital_invoicing.doctype.di_log.di_log import create_log

_NTN_PATTERN = re.compile(r"^\d{7}-?\d$")
_CNIC_PATTERN = re.compile(r"^\d{5}-?\d{7}-?\d$")
_CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


class POSFiscalError(frappe.ValidationError):
	"""Raised when POS fiscalization cannot be completed."""


@dataclass(frozen=True)
class POSSettings:
	enabled: bool
	environment: str
	pos_id: str
	bearer_token: str
	api_url: str


def fiscalize_invoice(doc):
	"""Submit a POS invoice to FBR and write the fiscal response back."""
	if not cint(doc.get("is_pos")):
		return

	pos_profile = cstr(doc.get("pos_profile") or "").strip()
	if not pos_profile:
		return

	if cstr(doc.get("di_integration_id") or "").strip():
		return

	settings = _get_pos_settings(pos_profile)
	if not settings.enabled:
		return

	payload = _build_payload(doc, settings)

	try:
		response_data = _post_invoice(doc, payload, settings)
	except Exception as e:
		create_log(
			doc.doctype, doc.name, payload, str(e),
			status="Error", api_type="POS Fiscal",
			title=f"POS Fiscal Error: {doc.name}",
		)
		frappe.throw(_("FBR POS API request failed: {0}").format(str(e)))

	invoice_number = _extract_value(response_data, "FBRInvoiceNumber", "InvoiceNumber")
	response_code = cstr(_extract_value(response_data, "Code", default="")).strip()
	response_message = cstr(
		_extract_value(response_data, "Response", "Message", "message", default="")
	).strip()

	if not invoice_number or (
		response_code and response_code not in {str(c) for c in POS_SUCCESS_CODES}
	):
		error_msg = response_message or _("FBR did not return a fiscal invoice number.")
		create_log(
			doc.doctype, doc.name, payload, response_data,
			status="Error", api_type="POS Fiscal",
			title=f"POS Fiscal Error: {doc.name}",
			error_message=error_msg,
		)
		raise POSFiscalError(error_msg)

	doc.di_integration_id = cstr(invoice_number).strip()
	doc.is_di_posted = 1
	doc.di_posting_datetime = now_datetime()

	create_log(
		doc.doctype, doc.name, payload, response_data,
		status="Success", api_type="POS Fiscal",
		title=f"POS Fiscal Success: {doc.name}",
		fbr_invoice_number=cstr(invoice_number).strip(),
	)


def _get_pos_settings(pos_profile):
	"""Load POS fiscal settings from POS Profile."""
	profile_doc = frappe.get_doc("POS Profile", pos_profile)
	enabled = cint(getattr(profile_doc, "enable_fbr_integration", 0))
	if not enabled:
		return POSSettings(
			enabled=False, environment="Sandbox",
			pos_id="", bearer_token="", api_url=POS_SANDBOX_URL,
		)

	environment = cstr(getattr(profile_doc, "fbr_environment", "Sandbox") or "Sandbox").strip()
	pos_id = cstr(getattr(profile_doc, "fbr_pos_id", "") or "").strip()
	bearer_token = cstr(profile_doc.get_password("fbr_bearer_token") or "").strip()
	api_url = (
		cstr(getattr(profile_doc, "fbr_api_url", "") or "").strip()
		or (POS_PROD_URL if environment.lower() == "production" else POS_SANDBOX_URL)
	)

	missing = []
	if not pos_id:
		missing.append(_("FBR POS ID"))
	if not bearer_token:
		missing.append(_("FBR Bearer Token"))

	if missing:
		raise POSFiscalError(
			_("FBR integration is enabled on POS Profile {0}, but these fields are missing: {1}").format(
				pos_profile, ", ".join(missing)
			)
		)

	return POSSettings(
		enabled=True, environment=environment,
		pos_id=pos_id, bearer_token=bearer_token, api_url=api_url,
	)


def _build_payload(doc, settings):
	"""Build FBR POS fiscal payload from invoice document."""
	is_return = cint(doc.get("is_return")) == 1
	invoice_type = POS_INVOICE_CREDIT if is_return else POS_INVOICE_NEW
	items = []
	total_sale_value = 0.0
	total_tax_charged = 0.0
	total_discount = abs(flt(doc.get("discount_amount")))
	total_quantity = 0.0

	for item in doc.get("items") or []:
		qty = abs(flt(item.get("qty")))
		if qty <= 0:
			continue

		item_code = cstr(item.get("item_code") or "").strip()
		pct_code = _get_pct_code(item_code)

		line_invoice_type = _resolve_item_invoice_type(is_return, item_code)
		actual_sale_value = abs(flt(item.get("base_net_amount") or item.get("net_amount")))
		gross_sale_value = abs(flt(item.get("price_list_rate") or item.get("rate"))) * qty
		line_discount = max(gross_sale_value - actual_sale_value, 0.0)
		line_tax_charged, line_tax_rate = _resolve_item_tax(item, doc, actual_sale_value)
		line_total = abs(flt(item.get("base_amount") or item.get("amount"))) or (
			actual_sale_value + line_tax_charged
		)

		items.append({
			"ItemCode": item_code,
			"ItemName": _sanitize(item.get("item_name") or item_code, 150),
			"Quantity": qty,
			"PCTCode": pct_code,
			"TaxRate": line_tax_rate,
			"SaleValue": actual_sale_value,
			"TotalAmount": line_total,
			"TaxCharged": line_tax_charged,
			"Discount": line_discount,
			"FurtherTax": 0.0,
			"InvoiceType": line_invoice_type,
			"RefUSIN": doc.get("return_against") if is_return else None,
		})

		total_sale_value += actual_sale_value
		total_tax_charged += line_tax_charged
		total_discount += line_discount
		total_quantity += qty

	buyer_ntn, buyer_cnic = _split_tax_identifier(doc.get("tax_id"))

	return {
		"InvoiceNumber": "",
		"POSID": int(settings.pos_id) if settings.pos_id.isdigit() else settings.pos_id,
		"USIN": _sanitize(doc.name, 50),
		"DateTime": _build_datetime(doc),
		"BuyerNTN": buyer_ntn,
		"BuyerCNIC": buyer_cnic,
		"BuyerName": _sanitize(doc.get("customer_name") or "", 150),
		"BuyerPhoneNumber": _sanitize(
			doc.get("contact_mobile") or doc.get("contact_phone") or "", 20
		),
		"TotalBillAmount": abs(flt(doc.get("base_rounded_total") or doc.get("base_grand_total"))),
		"TotalQuantity": total_quantity,
		"TotalSaleValue": total_sale_value,
		"TotalTaxCharged": total_tax_charged,
		"Discount": total_discount,
		"FurtherTax": 0.0,
		"PaymentMode": _resolve_payment_mode(doc),
		"RefUSIN": doc.get("return_against") if is_return else None,
		"InvoiceType": invoice_type,
		"Items": items,
	}


def _post_invoice(doc, payload, settings):
	"""POST the fiscal payload to FBR."""
	headers = {
		"Authorization": f"Bearer {settings.bearer_token}",
		"Accept": "application/json",
		"Content-Type": "application/json",
	}

	response = requests.post(
		settings.api_url,
		json=payload,
		headers=headers,
		timeout=30,
	)

	try:
		response_data = response.json()
		if not isinstance(response_data, dict):
			response_data = {"data": response_data}
	except ValueError:
		response_data = {"message": response.text}

	if response.status_code >= 400:
		message = cstr(
			_extract_value(response_data, "Response", "Message", "message", default=response.text)
		).strip()
		if response.status_code in {401, 403}:
			message = message or _("FBR rejected the request. Check your bearer token.")
		raise POSFiscalError(message or _("FBR rejected the invoice request."))

	return response_data


def _resolve_payment_mode(doc):
	"""Map Mode of Payment to FBR payment mode code (1-6)."""
	payments = [
		p for p in (doc.get("payments") or [])
		if abs(flt(p.get("amount"))) > 0
	]
	if len(payments) > 1:
		return PAYMENT_MODE_MIXED
	if not payments:
		return PAYMENT_MODE_CASH

	mode_name = cstr(payments[0].get("mode_of_payment") or "").strip()
	configured_code = cstr(
		frappe.db.get_value("Mode of Payment", mode_name, "fbr_payment_mode_code") or ""
	).strip()
	if configured_code:
		return cint(configured_code)

	mode_lower = mode_name.lower()
	if "cash" in mode_lower:
		return PAYMENT_MODE_CASH
	if any(k in mode_lower for k in ("card", "visa", "master")):
		return PAYMENT_MODE_CARD
	if any(k in mode_lower for k in ("gift", "voucher")):
		return PAYMENT_MODE_GIFT_VOUCHER
	if "loyalty" in mode_lower:
		return PAYMENT_MODE_LOYALTY
	if any(k in mode_lower for k in ("cheque", "check")):
		return PAYMENT_MODE_CHEQUE

	raise POSFiscalError(
		_("Mode of Payment {0} is not mapped to an FBR Payment Mode Code.").format(mode_name)
	)


def _resolve_item_invoice_type(is_return, item_code):
	"""Determine FBR invoice type for an item (1, 3, 11, or 12)."""
	is_3rd_schedule = cint(
		frappe.db.get_value("Item", item_code, "fbr_third_schedule") or 0
	)
	if is_3rd_schedule:
		return POS_INVOICE_3RD_SCHEDULE_CREDIT if is_return else POS_INVOICE_3RD_SCHEDULE_NEW
	return POS_INVOICE_CREDIT if is_return else POS_INVOICE_NEW


def _get_pct_code(item_code):
	"""Get the PCT/HS code for an item."""
	pct_code = cstr(
		frappe.db.get_value("Item", item_code, "customs_tariff_number") or ""
	).strip()
	if not pct_code:
		raise POSFiscalError(
			_("Item {0} is missing Customs Tariff Number (PCT Code).").format(item_code)
		)
	return pct_code


def _resolve_item_tax(item, doc, sale_value):
	"""Calculate tax amount and rate for an item."""
	base_amount = abs(flt(item.get("base_amount") or item.get("amount")))
	net_amount = abs(flt(item.get("base_net_amount") or item.get("net_amount")))

	if base_amount and net_amount and abs(base_amount - net_amount) > 0.0001:
		tax_charged = abs(base_amount - net_amount)
		rate = flt((tax_charged / sale_value) * 100, 3) if sale_value else 0.0
		return tax_charged, rate

	tax_rate = _get_item_tax_rate(item, doc)
	tax_charged = flt(sale_value * tax_rate / 100, 2) if sale_value and tax_rate else 0.0
	return tax_charged, tax_rate


def _get_item_tax_rate(item, doc):
	"""Get the effective tax rate for an item."""
	item_tax_rate = item.get("item_tax_rate")
	if item_tax_rate:
		if isinstance(item_tax_rate, str):
			try:
				item_tax_rate = json.loads(item_tax_rate)
			except ValueError:
				item_tax_rate = {}
		if isinstance(item_tax_rate, dict):
			return flt(sum(flt(v) for v in item_tax_rate.values()), 3)

	total_rate = 0.0
	percentage_types = {"On Net Total", "On Previous Row Amount", "On Previous Row Total"}
	for tax in doc.get("taxes") or []:
		if cstr(tax.get("charge_type") or "").strip() in percentage_types:
			total_rate += flt(tax.get("rate"))
	return flt(total_rate, 3)


def _split_tax_identifier(value):
	"""Split a tax ID into NTN and CNIC components."""
	tax_id = _sanitize(value, 20)
	if not tax_id:
		return None, None
	if _NTN_PATTERN.match(tax_id):
		return tax_id, None
	if _CNIC_PATTERN.match(tax_id):
		return None, tax_id
	return tax_id, None


def _build_datetime(doc):
	"""Build posting datetime string."""
	posting_date = cstr(doc.get("posting_date") or "").strip()
	posting_time = cstr(doc.get("posting_time") or "").strip() or now_datetime().strftime("%H:%M:%S")
	return f"{posting_date} {posting_time}".strip()


def _sanitize(value, max_length=None):
	"""Clean text for FBR API."""
	if value in (None, ""):
		return None
	text = _CONTROL_CHAR_PATTERN.sub("", cstr(value).strip())
	if max_length:
		text = text[:max_length]
	return text or None


def _extract_value(data, *keys, default=None):
	"""Extract the first non-empty value from a dict by trying multiple keys."""
	if not isinstance(data, dict):
		return default
	for key in keys:
		if key in data and data[key] not in (None, ""):
			return data[key]
	return default
