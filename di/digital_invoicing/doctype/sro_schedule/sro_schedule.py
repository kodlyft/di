import frappe
from frappe.model.document import Document


class SROSchedule(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		sro_desc: DF.Data
		sro_id: DF.Int
	# end: auto-generated types
	pass
