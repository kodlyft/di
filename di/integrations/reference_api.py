"""FBR Reference Data API integration.

Syncs reference data (provinces, HS codes, UOMs, transaction types,
SRO schedules, sale type rates) from FBR's PDI API endpoints.
"""
import frappe
import requests
from frappe import _
from frappe.utils import cstr

from di.constants import REF_BASE_V1, REF_BASE_V2
from di.digital_invoicing.doctype.di_log.di_log import create_log


@frappe.whitelist()
def sync_provinces(company=None):
	"""Sync provinces from FBR API."""
	token = _get_token(company)
	url = f"{REF_BASE_V1}/provinces"
	data = _make_get_request(url, token, "provinces")

	count = 0
	for item in data:
		province_code = item.get("provinceId") or item.get("id")
		province_name = item.get("provinceName") or item.get("name")
		if not province_name:
			continue

		if frappe.db.exists("Province", province_name):
			doc = frappe.get_doc("Province", province_name)
			doc.province_code = province_code
			doc.save(ignore_permissions=True)
		else:
			frappe.get_doc({
				"doctype": "Province",
				"province_name": province_name,
				"province_code": province_code,
			}).insert(ignore_permissions=True)
		count += 1

	frappe.db.commit()
	return {"message": _("{0} provinces synced").format(count)}


@frappe.whitelist()
def sync_hs_codes(company=None):
	"""Sync HS codes from FBR API."""
	token = _get_token(company)
	url = f"{REF_BASE_V1}/itemdesccode"
	data = _make_get_request(url, token, "HS codes")

	count = 0
	for item in data:
		hs_code = cstr(item.get("hsCode") or item.get("code") or "").strip()
		if not hs_code:
			continue

		description = item.get("description") or item.get("itemDescription") or ""
		uom_name = item.get("uom") or item.get("uomName") or ""

		uom_link = ""
		if uom_name and frappe.db.exists("HS Uom", uom_name):
			uom_link = uom_name

		if frappe.db.exists("HS Code", hs_code):
			doc = frappe.get_doc("HS Code", hs_code)
			doc.description = description
			if uom_link:
				doc.uom = uom_link
			doc.save(ignore_permissions=True)
		else:
			frappe.get_doc({
				"doctype": "HS Code",
				"hs_code": hs_code,
				"description": description,
				"uom": uom_link,
			}).insert(ignore_permissions=True)
		count += 1

	frappe.db.commit()
	return {"message": _("{0} HS codes synced").format(count)}


@frappe.whitelist()
def sync_uoms(company=None):
	"""Sync UOMs from FBR API."""
	token = _get_token(company)
	url = f"{REF_BASE_V1}/uom"
	data = _make_get_request(url, token, "UOMs")

	count = 0
	for item in data:
		uom_id = item.get("uomId") or item.get("id")
		uom_name = item.get("uomName") or item.get("name")
		if not uom_name:
			continue

		if frappe.db.exists("HS Uom", uom_name):
			doc = frappe.get_doc("HS Uom", uom_name)
			doc.uom_id = uom_id
			doc.save(ignore_permissions=True)
		else:
			frappe.get_doc({
				"doctype": "HS Uom",
				"uom_name": uom_name,
				"uom_id": uom_id,
			}).insert(ignore_permissions=True)
		count += 1

	frappe.db.commit()
	return {"message": _("{0} UOMs synced").format(count)}


@frappe.whitelist()
def sync_transaction_types(company=None):
	"""Sync transaction types from FBR API."""
	token = _get_token(company)
	url = f"{REF_BASE_V1}/transtypecode"
	data = _make_get_request(url, token, "transaction types")

	count = 0
	for item in data:
		type_id = item.get("transTypeId") or item.get("id")
		desc = item.get("transTypeDesc") or item.get("description")
		if not desc:
			continue

		if frappe.db.exists("Transaction Type", desc):
			doc = frappe.get_doc("Transaction Type", desc)
			doc.transaction_type_id = type_id
			doc.save(ignore_permissions=True)
		else:
			frappe.get_doc({
				"doctype": "Transaction Type",
				"transaction_desc": desc,
				"transaction_type_id": type_id,
			}).insert(ignore_permissions=True)
		count += 1

	frappe.db.commit()
	return {"message": _("{0} transaction types synced").format(count)}


@frappe.whitelist()
def sync_sro_item_codes(company=None):
	"""Sync SRO item codes from FBR API."""
	token = _get_token(company)
	url = f"{REF_BASE_V1}/sroitemcode"
	data = _make_get_request(url, token, "SRO item codes")

	count = 0
	for item in data:
		sro_item_id = item.get("sroItemId") or item.get("id")
		sro_item_desc = item.get("sroItemDesc") or item.get("description") or ""
		sro_schedule_name = item.get("sroSchedule") or item.get("scheduleName") or ""

		sro_schedule_link = ""
		if sro_schedule_name and frappe.db.exists("SRO Schedule", sro_schedule_name):
			sro_schedule_link = sro_schedule_name

		existing = frappe.db.exists("SRO Item", {"sro_item_id": sro_item_id})
		if existing:
			doc = frappe.get_doc("SRO Item", existing)
			doc.sro_item_desc = sro_item_desc
			if sro_schedule_link:
				doc.sro_schedule = sro_schedule_link
			doc.save(ignore_permissions=True)
		else:
			frappe.get_doc({
				"doctype": "SRO Item",
				"sro_item_id": sro_item_id,
				"sro_item_desc": sro_item_desc,
				"sro_schedule": sro_schedule_link,
			}).insert(ignore_permissions=True)
		count += 1

	frappe.db.commit()
	return {"message": _("{0} SRO item codes synced").format(count)}


@frappe.whitelist()
def sync_sro_schedules(rate_id=None, date=None, origination_supplier=None, company=None):
	"""Sync SRO schedules from FBR API."""
	token = _get_token(company)
	url = f"{REF_BASE_V1}/SroSchedule"

	params = {}
	if rate_id:
		params["rateId"] = rate_id
	if date:
		params["date"] = date
	if origination_supplier:
		params["originationSupplier"] = origination_supplier

	data = _make_get_request(url, token, "SRO schedules", params=params)

	count = 0
	for item in data:
		sro_id = item.get("sroId") or item.get("id")
		sro_desc = item.get("sroDesc") or item.get("description")
		if not sro_desc:
			continue

		if frappe.db.exists("SRO Schedule", sro_desc):
			doc = frappe.get_doc("SRO Schedule", sro_desc)
			doc.sro_id = sro_id
			doc.save(ignore_permissions=True)
		else:
			frappe.get_doc({
				"doctype": "SRO Schedule",
				"sro_desc": sro_desc,
				"sro_id": sro_id,
			}).insert(ignore_permissions=True)
		count += 1

	frappe.db.commit()
	return {"message": _("{0} SRO schedules synced").format(count)}


@frappe.whitelist()
def sync_sale_type_rates(date=None, trans_type_id=None, origination_supplier=None, company=None):
	"""Sync sale type to rate mappings from FBR API v2."""
	token = _get_token(company)
	url = f"{REF_BASE_V2}/SaleTypeToRate"

	params = {}
	if date:
		params["date"] = date
	if trans_type_id:
		params["transTypeId"] = trans_type_id
	if origination_supplier:
		params["originationSupplier"] = origination_supplier

	data = _make_get_request(url, token, "sale type rates", params=params)
	return {"data": data, "message": _("{0} records received").format(len(data))}


def _get_token(company=None):
	"""Get the DI bearer token from settings."""
	from di.digital_invoicing.doctype.di_settings.di_settings import get_settings

	if not company:
		company = frappe.defaults.get_global_default("company")
	if not company:
		frappe.throw(_("No company specified for reference data sync"))

	settings = get_settings(company)
	if not settings:
		frappe.throw(_("DI Settings not found for company {0}").format(company))

	return settings.get_password("access_token")


def _make_get_request(url, token, data_type, params=None):
	"""Make an authenticated GET request to the FBR reference API."""
	try:
		response = requests.get(
			url,
			params=params,
			headers={
				"Authorization": f"Bearer {token}",
				"Accept": "application/json",
			},
			timeout=30,
		)
	except requests.RequestException as e:
		create_log(
			"DI Settings", "", {"url": url, "params": params}, str(e),
			status="Error", api_type="Reference",
			title=f"Reference Sync Error: {data_type}",
		)
		frappe.throw(_("FBR reference API request failed for {0}: {1}").format(data_type, str(e)))

	if response.status_code == 401:
		frappe.throw(_("FBR API returned 401 Unauthorized. Check your access token."))
	if response.status_code >= 400:
		frappe.throw(
			_("FBR reference API returned {0} for {1}").format(response.status_code, data_type)
		)

	try:
		data = response.json()
	except ValueError:
		frappe.throw(_("Invalid JSON response from FBR for {0}").format(data_type))

	if isinstance(data, dict):
		for key in ("data", "result", "results", "items"):
			if key in data and isinstance(data[key], list):
				data = data[key]
				break
		else:
			data = [data]

	if not isinstance(data, list):
		data = [data] if data else []

	create_log(
		"DI Settings", "", {"url": url, "params": params}, {"count": len(data)},
		status="Success", api_type="Reference",
		title=f"Reference Sync: {data_type}",
	)

	return data
