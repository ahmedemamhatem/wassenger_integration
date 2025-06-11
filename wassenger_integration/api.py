import frappe
import requests

@frappe.whitelist()
def send_whatsapp_message(docname):
    doc = frappe.get_doc("WH Massage", docname)
    api_key = frappe.db.get_single_value("Wassenger Settings", "api_key")
    url = "https://api.wassenger.com/v1/messages"
    headers_json = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    sent = False
    file_tried = False

    # 1. Try to send PDF if present and is a PDF (NO CAPTION!)
    if getattr(doc, "file", None):
        file_url = frappe.utils.get_url(doc.file)
        file_name = doc.file.split('/')[-1]
        if file_name.lower().endswith('.pdf'):
            file_tried = True
            data = {
                "phone": doc.phone,
                "mediaUrl": file_url,
                "filename": file_name
            }
            try:
                resp = requests.post(url, headers=headers_json, json=data)
                if resp.status_code in [200, 201]:
                    resp_json = resp.json()
                    message_id = resp_json.get("id")
                    frappe.db.set_value(doc.doctype, doc.name, {
                        "wassenger_message_id": message_id,
                        "status": "Sent"
                    })
                    frappe.msgprint(f"PDF {file_name} sent successfully as WhatsApp attachment.")
                    sent = True
                    return
                else:
                    frappe.log_error(f"Failed to send PDF {file_name}. Response: {resp.text}")
                    frappe.msgprint(f"Failed to send PDF. Will send as plain text message.")
            except Exception as e:
                frappe.log_error(f"Error sending PDF file: {str(e)}")
                frappe.msgprint(f"Error sending PDF file. Will send as plain text message.")
        else:
            frappe.log_error(f"File {file_name} is not a PDF. Only PDF attachments are allowed.")
            frappe.msgprint(f"File {file_name} is not a PDF. Only PDF attachments are allowed.")

    # 2. Try to send plain text if not sent above and message exists
    if not sent and doc.send_message:
        data = {
            "phone": doc.phone,
            "message": doc.send_message
        }
        try:
            resp = requests.post(url, headers=headers_json, json=data)
            if resp.status_code in [200, 201]:
                resp_json = resp.json()
                message_id = resp_json.get("id")
                frappe.db.set_value(doc.doctype, doc.name, {
                    "wassenger_message_id": message_id,
                    "status": "Sent"
                })
                if file_tried:
                    frappe.msgprint("WhatsApp message sent successfully (without file).")
                else:
                    frappe.msgprint("WhatsApp message sent successfully.")
                sent = True
            else:
                frappe.db.set_value(doc.doctype, doc.name, "status", "Failed")
                frappe.log_error(f"Failed to send WhatsApp message. Response: {resp.text}")
                frappe.msgprint("Failed to send WhatsApp message. See error log.")
        except Exception as e:
            frappe.db.set_value(doc.doctype, doc.name, "status", "Failed")
            frappe.log_error(f"Error sending WhatsApp message: {str(e)}")
            frappe.msgprint("Error sending WhatsApp message. See error log.")

    if not sent:
        frappe.db.set_value(doc.doctype, doc.name, "status", "Failed")
        frappe.msgprint("WhatsApp message could not be sent. See error log.")


@frappe.whitelist(allow_guest=True)
def wassenger_webhook():
    """
    Webhook endpoint for Wassenger status updates.
    Point your Wassenger 'status update' webhooks here.
    """
    import json
    if frappe.request.method == "POST":
        try:
            data = frappe.local.form_dict or json.loads(frappe.request.data or '{}')
        except Exception:
            data = {}

        # Try to get message id and status from the payload
        message_id = data.get("id") or data.get("message", {}).get("id")
        status = data.get("status") or data.get("event")
        if not message_id or not status:
            return "Missing message id or status"

        wh_massage = frappe.get_all("WH Massage", filters={"wassenger_message_id": message_id}, fields=["name"])
        if wh_massage:
            frappe.db.set_value("WH Massage", wh_massage[0].name, "status", status.capitalize())
            frappe.db.commit()
            return "OK"
        return "Message not found"
    return "Invalid method"


@frappe.whitelist(allow_guest=True)
def wassenger_inbound_webhook():
    """
    Webhook endpoint for incoming WhatsApp messages (replies).
    Point your Wassenger 'reply' webhooks here.
    """
    import json
    if frappe.request.method == "POST":
        try:
            data = frappe.local.form_dict or json.loads(frappe.request.data or '{}')
        except Exception:
            data = {}

        # Adjust these keys based on your actual Wassenger payload
        message_id = data.get("id") or data.get("message", {}).get("id")
        from_number = data.get("from") or data.get("contact", {}).get("phone")
        # Try all possible keys for text
        message_text = (
            data.get("message") or
            (data.get("body", {}).get("text") if isinstance(data.get("body"), dict) else None) or
            data.get("text")
        )
        timestamp = data.get("timestamp") or data.get("created_at")

        if not from_number or not message_text:
            frappe.log_error(f"Invalid inbound webhook payload: {data}")
            return "Invalid payload"

        # Insert as type 'in' (incoming/reply)
        doc = frappe.get_doc({
            "doctype": "WH Massage",
            "wassenger_message_id": message_id,
            "phone": from_number,
            "send_message": message_text,
            "status": "Received",
            "type": "in"
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return "OK"
    return "Invalid method"