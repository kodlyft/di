import frappe
from frappe import _
from frappe.model.document import Document


class DISettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from di.digital_invoicing.doctype.company_sale_type.company_sale_type import CompanySaleType
		from di.digital_invoicing.doctype.company_sandbox_scenario.company_sandbox_scenario import CompanySandboxScenario
		from frappe.types import DF

		access_token: DF.Password | None
		address: DF.Data | None
		annexure_id: DF.Data | None
		auto_post_on_submit: DF.Check
		company: DF.Link
		enable_pos_fiscal: DF.Check
		enabled: DF.Check
		ntn_cnic: DF.Data | None
		pos_bearer_token: DF.Password | None
		pos_environment: DF.Literal["Sandbox", "Production"]
		pos_id: DF.Data | None
		province: DF.Link | None
		sale_types: DF.Table[CompanySaleType]
		scenarios: DF.Table[CompanySandboxScenario]
		strn_no: DF.Data | None
		sync_mode: DF.Literal["Production", "Sandbox"]
	# end: auto-generated types
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
