import frappe
from frappe import _
from frappe.model.document import Document


class DISettings(Document):
	def validate(self):
		self._validate_duplicate_sale_types()

	def _validate_duplicate_sale_types(self):
		seen = set()
		for row in self.get("sale_types") or []:
			if row.sale_type in seen:
				frappe.throw(_("Duplicate sale type '{0}' in row {1}").format(row.sale_type, row.idx))
			seen.add(row.sale_type)


@frappe.whitelist()
def is_enabled(company):
	"""Check if Digital Invoicing is enabled for the given company."""
	return frappe.db.get_value("DI Settings", {"company": company}, "enabled")


def get_settings(company):
	"""Get DI Settings document for the given company."""
	if not frappe.db.exists("DI Settings", {"company": company}):
		return None
	return frappe.get_doc("DI Settings", company)
