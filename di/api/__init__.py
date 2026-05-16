from inspect import signature

import frappe
from frappe import _


@frappe.whitelist()
def resync_invoice(doctype, name):
	"""Re-post an invoice to FBR DI after corrections."""
	from di.integrations.di_api import post_invoice

	doc = frappe.get_doc(doctype, name)
	post_invoice(doc, resync=True)
	return {"success": True, "message": _("Invoice re-synced successfully")}


@frappe.whitelist()
def validate_invoice(doctype, name):
	"""Validate invoice with FBR without posting."""
	from di.integrations.di_api import validate_invoice as _validate

	doc = frappe.get_doc(doctype, name)
	return _validate(doc)


@frappe.whitelist()
def get_invoice_preview(doctype, name):
	"""Preview the DI payload without posting."""
	from di.integrations.di_api import build_di_payload

	doc = frappe.get_doc(doctype, name)
	return build_di_payload(doc)


@frappe.whitelist()
def verify_buyer(customer):
	"""Check buyer registration status via STATL."""
	from di.integrations.statl import get_registration_type

	ntn_cnic = frappe.db.get_value("Customer", customer, "ntn_cnic")
	if not ntn_cnic:
		frappe.throw(_("Customer {0} does not have NTN/CNIC set").format(customer))
	return get_registration_type(ntn_cnic)


@frappe.whitelist()
def sync_reference_data(data_type, **kwargs):
	"""Trigger reference data sync from FBR."""
	from di.integrations import reference_api

	sync_map = {
		"provinces": reference_api.sync_provinces,
		"hs_codes": reference_api.sync_hs_codes,
		"uoms": reference_api.sync_uoms,
		"transaction_types": reference_api.sync_transaction_types,
		"sro_item_codes": reference_api.sync_sro_item_codes,
	}

	func = sync_map.get(data_type)
	if not func:
		frappe.throw(_("Unknown data type: {0}").format(data_type))

	supported_params = signature(func).parameters
	filtered_kwargs = {key: value for key, value in kwargs.items() if key in supported_params}
	return func(**filtered_kwargs)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_sale_types_for_company(doctype, txt, searchfield, start, page_len, filters):
	"""Query filter for sale type dropdown - returns only company-configured types."""
	company = filters.get("company")
	if not company:
		return []

	return frappe.db.sql(
		"""
		SELECT cst.sale_type
		FROM `tabCompany Sale Type` cst
		WHERE cst.parent = %(company)s
			AND cst.parenttype = 'DI Settings'
			AND cst.sale_type LIKE %(txt)s
		ORDER BY cst.sale_type
		LIMIT %(page_len)s OFFSET %(start)s
		""",
		{
			"company": company,
			"txt": f"%{txt}%",
			"start": start,
			"page_len": page_len,
		},
	)
