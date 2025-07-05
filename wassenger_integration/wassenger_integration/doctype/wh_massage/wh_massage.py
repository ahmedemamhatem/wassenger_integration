import frappe
from frappe.model.document import Document

class WHMassage(Document):
    def after_insert(self):
        """
        After inserting a WH Massage document:
        - Set the type to 'out'.
        - Validate the phone number for WhatsApp delivery:
          - Must be a non-empty string.
          - Must start with '+' (country code required, e.g. +14155552671).
          - Only digits allowed after '+'.
          - Minimum 10 digits after '+'.
        - If the phone number is missing or invalid, set status to 'Failed' and add a comment explaining why.
        - If the phone number is valid, set status to 'Pending'.
        """
        frappe.db.set_value(self.doctype, self.name, "type", "out")
        phone = getattr(self, "phone", None)

        def is_valid_whatsapp_number(number):
            """
            Check if the phone number is in the correct WhatsApp format:
            - Starts with '+'
            - Only digits after '+'
            - At least 10 digits after '+'
            """
            if not number or not isinstance(number, str):
                return False
            if not number.startswith('+'):
                return False
            digits = number[1:]
            if not digits.isdigit():
                return False
            if len(digits) < 10:
                return False
            return True

        if not is_valid_whatsapp_number(phone):
            frappe.db.set_value(self.doctype, self.name, "status", "Failed")
            self.add_comment(
                "Comment",
                text=(
                    "WhatsApp message not sent: phone number is missing, not valid, "
                    "or does not include country code (e.g. +14155552671)."
                )
            )
        else:
            frappe.db.set_value(self.doctype, self.name, "status", "Pending")
            self.reload()

    def on_submit(self):
        """
        On submit of WH Massage:
        - If status is NOT "Failed", send WhatsApp message.
        - If status is "Failed", do nothing.
        - If sending fails, set status to 'Failed' and add a comment.
        """
        # Reload status from DB to ensure we have the latest value
        status = frappe.db.get_value(self.doctype, self.name, "status")
        if status != "Failed":
            try:
                from wassenger_integration.api import send_whatsapp_message
                send_whatsapp_message(self.name)
            except Exception as e:
                self.db_set("status", "Failed")
                frappe.log_error(f"Error sending WhatsApp for WH Massage {self.name}: {str(e)}")
                self.add_comment(
                    "Comment",
                    text=f"WhatsApp sending failed due to system error. See error log. ({str(e)})"
                )