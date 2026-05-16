import frappe
from frappe.model.document import Document


class SandboxScenario(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.Data | None
		sale_type: DF.Link | None
		scenario_id: DF.Data
	# end: auto-generated types
	pass
