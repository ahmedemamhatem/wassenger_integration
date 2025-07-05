import frappe
import requests
import os

def get_wassenger_settings():
    settings = frappe.get_single("Wassenger Settings")
    return {
        "api_key": settings.api_key,
        "device_id": getattr(settings, "device_id", None),  # If needed for your plan
        "allow_send_pdf_attachment": settings.allow_send_pdf_attachment
    }

def upload_file_to_wassenger(file_url, file_name, api_key):
    url = "https://api.wassenger.com/v1/files"
    payload = {
        "url": file_url,
        "format": "native"
    }
    headers = {
        "content-type": "application/json",
        "token": api_key
    }
    response = requests.post(url, json=payload, headers=headers)
    try:
        r = response.json()
    except Exception:
        raise Exception("Invalid response from Wassenger file upload: " + response.text)
    # Success: returns a list with dict
    if isinstance(r, list) and r and r[0].get("id"):
        return r[0]["id"]
    # Already uploaded: status 409
    elif isinstance(r, dict) and r.get("status") == 409 and r.get("meta", {}).get("file"):
        return r["meta"]["file"]
    else:
        frappe.log_error("Wassenger upload error: " + str(r))
        raise Exception("Failed to upload file to WhatsApp: " + str(r))

@frappe.whitelist()
def send_whatsapp_message(docname: str) -> None:
    """
    Send a WhatsApp message via Wassenger using the details from a 'WH Massage' doc.
    If PDF is allowed and present: upload PDF, then send as attachment.
    Otherwise, send message as text.
    """
    doc = frappe.get_doc("WH Massage", docname)

    # Early return if status is already 'Failed'
    if getattr(doc, "status", None) == "Failed":
        frappe.msgprint("WhatsApp sending skipped: document marked as Failed due to invalid phone or other reason.")
        return

    # Get settings and API key
    settings = get_wassenger_settings()
    api_key = settings["api_key"]
    allow_send_pdf_attachment = settings["allow_send_pdf_attachment"]

    sent = False
    file_tried = False

    # Step 1: Try to send PDF file (upload + send)
    if allow_send_pdf_attachment and getattr(doc, "file", None):
        file_url = frappe.utils.get_url(doc.file)
        file_name = os.path.basename(doc.file)
        if file_name.lower().endswith('.pdf'):
            file_tried = True
            try:
                # Upload the file and get file_id
                file_id = upload_file_to_wassenger(file_url, file_name, api_key)
                # Now send message referencing this file
                url = "https://api.wassenger.com/v1/messages"
                data = {
                    "phone": doc.phone,
                    "media": {"file": file_id}
                }
                headers = {
                    "content-type": "application/json",
                    "token": api_key
                }
                resp = requests.post(url, json=data, headers=headers, timeout=15)
                if resp.status_code in (200, 201):
                    message_id = resp.json().get("id")
                    frappe.db.set_value(doc.doctype, doc.name, {
                        "wassenger_message_id": message_id,
                        "status": "Sent"
                    })
                    frappe.msgprint(f"PDF <b>{file_name}</b> sent successfully as WhatsApp attachment.")
                    sent = True
                    return
                else:
                    frappe.log_error(f"Wassenger PDF send failed [{docname}]: {resp.status_code} {resp.text}")
                    frappe.msgprint(
                        f"Failed to send PDF via WhatsApp (Status {resp.status_code}). Will attempt plain text message."
                    )
            except Exception as e:
                frappe.log_error(f"Error uploading/sending WhatsApp PDF [{docname}]: {str(e)}")
                frappe.msgprint("Error sending PDF file. Will attempt plain text message.")
        else:
            frappe.log_error(f"File {file_name} in {docname} is not a PDF. Only PDF attachments are allowed.")
            frappe.msgprint(f"File <b>{file_name}</b> is not a PDF. Only PDF attachments are allowed.")

    # Step 2: Send plain text message if not sent already
    if not sent and getattr(doc, "send_message", None):
        url = "https://api.wassenger.com/v1/messages"
        data = {
            "phone": doc.phone,
            "message": doc.send_message
        }
        headers = {
            "content-type": "application/json",
            "token": api_key
        }
        try:
            resp = requests.post(url, json=data, headers=headers, timeout=15)
            if resp.status_code in (200, 201):
                message_id = resp.json().get("id")
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
                frappe.log_error(f"Wassenger text send failed [{docname}]: {resp.status_code} {resp.text}")
                frappe.msgprint("Failed to send WhatsApp message (text). See error log.")
        except Exception as e:
            frappe.db.set_value(doc.doctype, doc.name, "status", "Failed")
            frappe.log_error(f"Error sending WhatsApp text [{docname}]: {str(e)}")
            frappe.msgprint("Error sending WhatsApp message. See error log.")

    # Final fallback if nothing was sent
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
def whatsapp_reply():
    """
    Receives inbound WhatsApp messages from Wassenger and inserts as inbound message in ERP.
    """
    data = frappe.request.get_json()
    if not data:
        frappe.local.response.http_status_code = 400
        return {"error": "No JSON data received"}

    # Supported event type for inbound message
    if data.get("event") != "message:in:new":
        frappe.local.response.http_status_code = 400
        return {"error": "Not an inbound message event"}

    data_block = data.get("data", {})

    # Prepare fields from webhook payload
    message_id = data_block.get("id")
    phone_from = data_block.get("fromNumber")
    phone_to = data_block.get("toNumber")
    body = data_block.get("body")
    timestamp = data_block.get("timestamp")
    contact = data_block.get("chat", {}).get("contact", {})
    contact_name = contact.get("displayName") or contact.get("name")
    contact_phone = contact.get("phone")
    wa_status = data_block.get("status")
    ack = data_block.get("ack")
    event_type = data.get("event")

    # Optionally, fetch more fields as needed for your DocType

    # Insert inbound message as 'type = "in"'
    doc = frappe.get_doc({
        "doctype": "WH Massage",     # Use your actual DocType name
        "wassenger_message_id": message_id,
        "type": "in",
        "phone": phone_from,
        "send_message": body,
        "status": wa_status
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {"message": "Inbound WhatsApp message saved", "docname": doc.name}


@frappe.whitelist(allow_guest=True)
def whatsapp_status_update():
    """
    Receives WhatsApp message status updates from Wassenger and updates WH Massage status in ERP.
    Uses the exact 'ack' value from 'data.ack' in the webhook payload.
    """
    data = frappe.request.get_json()
    if not data:
        frappe.local.response.http_status_code = 400
        return {"error": "No JSON data received"}

    message_id = data.get("id")
    data_block = data.get("data", {})
    ack = data_block.get("ack")

    if not message_id or not ack:
        frappe.local.response.http_status_code = 400
        return {"error": "Missing 'id' or 'data.ack' in payload"}

    # Find WH Massage with corresponding wassenger_message_id
    wh_massage = frappe.get_all(
        "WH Massage",
        filters={"wassenger_message_id": message_id},
        fields=["name"]
    )

    if not wh_massage:
        frappe.local.response.http_status_code = 404
        return {"error": f"No WH Massage found with wassenger_message_id '{message_id}'"}

    # Directly set status to the exact ack value from data
    doc = frappe.get_doc("WH Massage", wh_massage[0].name)
    doc.status = ack
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"message": f"Status for message {message_id} updated to {ack}"}