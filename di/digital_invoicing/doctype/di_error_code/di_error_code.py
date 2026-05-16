import frappe
from frappe.model.document import Document


class DIErrorCode(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		category: DF.Literal["Sales", "Purchase", "General"]
		description: DF.Text | None
		error_code: DF.Data
		message: DF.Data | None
	# end: auto-generated types
	pass
