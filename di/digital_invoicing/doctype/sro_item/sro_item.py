import frappe
from frappe.model.document import Document


class SROItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		sro_item_desc: DF.Data | None
		sro_item_id: DF.Int
		sro_schedule: DF.Link | None
	# end: auto-generated types

	pass
