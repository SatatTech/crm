# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document

from crm.fcrm.doctype.crm_lead.crm_lead import set_communication_status_replied


class FCRMNote(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		content: DF.TextEditor | None
		reference_docname: DF.DynamicLink | None
		reference_doctype: DF.Link | None
		title: DF.Data
	# end: auto-generated types

	@staticmethod
	def default_list_data():
		rows = [
			"name",
			"title",
			"content",
			"reference_doctype",
			"reference_docname",
			"owner",
			"modified",
		]
		return {"columns": [], "rows": rows}

	def after_insert(self):
		if self.reference_doctype and self.reference_docname:
			set_communication_status_replied(self.reference_doctype, self.reference_docname)
