"""FBR STATL (Sales Tax Active Taxpayer List) verification.

Verifies buyer/seller registration status with FBR.
"""
import frappe
import requests
from frappe import _
from frappe.utils import cstr, today

from di.constants import STATL_BASE_URL
from di.digital_invoicing.doctype.di_log.di_log import create_log


@frappe.whitelist()
def check_status(registration_no, date=None, company=None):
	"""Check registration status via STATL API.

	Args:
		registration_no: NTN or CNIC number
		date: Date to check against (defaults to today)
		company: Company for token lookup
	"""
	if not registration_no:
		frappe.throw(_("Registration number is required"))

	token = _get_token(company)
	url = f"{STATL_BASE_URL}/statl"
	payload = {
		"registrationNo": cstr(registration_no).strip(),
		"date": cstr(date or today()),
	}

	try:
		response = requests.post(
			url,
			json=payload,
			headers={
				"Authorization": f"Bearer {token}",
				"Content-Type": "application/json",
				"Accept": "application/json",
			},
			timeout=30,
		)
	except requests.RequestException as e:
		create_log(
			"Customer", "", payload, str(e),
			status="Error", api_type="STATL",
			title=f"STATL Error: {registration_no}",
		)
		frappe.throw(_("STATL API request failed: {0}").format(str(e)))

	if response.status_code == 401:
		frappe.throw(_("FBR STATL API returned 401 Unauthorized. Check your access token."))

	try:
		result = response.json()
	except ValueError:
		frappe.throw(_("Invalid response from STATL API"))

	create_log(
		"Customer", "", payload, result,
		status="Success" if response.status_code == 200 else "Error",
		api_type="STATL",
		title=f"STATL Check: {registration_no}",
	)

	return result


@frappe.whitelist()
def get_registration_type(registration_no, company=None):
	"""Get buyer registration type (Registered/Unregistered) from FBR.

	Args:
		registration_no: NTN or CNIC number
		company: Company for token lookup
	"""
	if not registration_no:
		frappe.throw(_("Registration number is required"))

	token = _get_token(company)
	url = f"{STATL_BASE_URL}/Get_Reg_Type"
	payload = {
		"registrationNo": cstr(registration_no).strip(),
	}

	try:
		response = requests.post(
			url,
			json=payload,
			headers={
				"Authorization": f"Bearer {token}",
				"Content-Type": "application/json",
				"Accept": "application/json",
			},
			timeout=30,
		)
	except requests.RequestException as e:
		create_log(
			"Customer", "", payload, str(e),
			status="Error", api_type="STATL",
			title=f"STATL Reg Type Error: {registration_no}",
		)
		frappe.throw(_("STATL registration type request failed: {0}").format(str(e)))

	if response.status_code == 401:
		frappe.throw(_("FBR STATL API returned 401 Unauthorized. Check your access token."))

	try:
		result = response.json()
	except ValueError:
		frappe.throw(_("Invalid response from STATL API"))

	create_log(
		"Customer", "", payload, result,
		status="Success" if response.status_code == 200 else "Error",
		api_type="STATL",
		title=f"STATL Reg Type: {registration_no}",
	)

	return result


def _get_token(company=None):
	"""Get bearer token from DI Settings."""
	from di.digital_invoicing.doctype.di_settings.di_settings import get_settings

	if not company:
		company = frappe.defaults.get_global_default("company")
	if not company:
		frappe.throw(_("No company specified for STATL verification"))

	settings = get_settings(company)
	if not settings:
		frappe.throw(_("DI Settings not found for company {0}").format(company))

	return settings.get_password("access_token")
