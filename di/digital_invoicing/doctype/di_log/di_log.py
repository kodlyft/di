import json

import frappe
from frappe.model.document import Document


class DILog(Document):
	pass


def create_log(
	doctype,
	docname,
	payload,
	response,
	status="Success",
	title="",
	api_type="DI Post",
	error_code="",
	error_message="",
	fbr_invoice_number="",
):
	"""Create a DI Log entry for audit trail."""
	frappe.get_doc(
		{
			"doctype": "DI Log",
			"title": title or f"{status}: {doctype} {docname}",
			"document_type": doctype,
			"document_name": docname,
			"api_type": api_type,
			"status": status,
			"payload": json.dumps(payload, default=str, indent=2)
			if isinstance(payload, dict)
			else str(payload),
			"response": json.dumps(response, default=str, indent=2)
			if isinstance(response, dict)
			else str(response),
			"error_code": error_code,
			"error_message": error_message,
			"fbr_invoice_number": fbr_invoice_number,
		}
	).insert(ignore_permissions=True)
