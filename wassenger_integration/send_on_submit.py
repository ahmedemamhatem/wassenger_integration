import frappe

def get_professional_whatsapp_message(doc, party_type):
    """
    Build a detailed, professional WhatsApp message for document submission,
    skipping lines where data is missing/empty/None.
    """
    company = getattr(doc, "company", None) or frappe.get_single("Global Defaults").default_company

    def add(label, value):
        # Returns formatted line only if value is meaningful
        if value and str(value).strip() and str(value).strip().lower() != "none":
            return f"{label}: {value}"
        return None

    if doc.doctype == "Sales Invoice":
        lines = [
            f"Dear {getattr(doc, 'customer_name', party_type)},",
            "",
            f"Your Sales Invoice *{doc.name}* has been submitted.",
            add("Date", frappe.utils.formatdate(doc.posting_date)),
            add("Amount", frappe.utils.fmt_money(doc.grand_total, currency=doc.currency)),
            add("Due Date", frappe.utils.formatdate(getattr(doc, 'due_date', '')) if getattr(doc, 'due_date', None) else None),
            add("Customer", getattr(doc, 'customer', '')),
            add("Contact", getattr(doc, 'contact_display', '') or getattr(doc, 'contact_person', '') or ''),
            add("Billing Address", getattr(doc, 'customer_address', '')),
            "",
            "Thank you for your business!",
            "",
            f"Best regards,\n{company}"
        ]
    elif doc.doctype == "Purchase Invoice":
        lines = [
            f"Dear {getattr(doc, 'supplier_name', party_type)},",
            "",
            f"Your Purchase Invoice *{doc.name}* has been recorded.",
            add("Date", frappe.utils.formatdate(doc.posting_date)),
            add("Amount", frappe.utils.fmt_money(doc.grand_total, currency=doc.currency)),
            add("Due Date", frappe.utils.formatdate(getattr(doc, 'due_date', '')) if getattr(doc, 'due_date', None) else None),
            add("Supplier", getattr(doc, 'supplier', '')),
            add("Contact", getattr(doc, 'contact_display', '') or getattr(doc, 'contact_person', '') or ''),
            add("Billing Address", getattr(doc, 'supplier_address', '')),
            "",
            "Thank you for your cooperation.",
            "",
            f"Best regards,\n{company}"
        ]
    elif doc.doctype == "Delivery Note":
        try:
            total_qty = sum([row.qty for row in getattr(doc, 'items', [])])
        except Exception:
            total_qty = None
        lines = [
            f"Dear {getattr(doc, 'customer_name', party_type)},",
            "",
            f"Your Delivery Note *{doc.name}* has been submitted.",
            add("Date", frappe.utils.formatdate(doc.posting_date)),
            add("Total Quantity", total_qty if total_qty else None),
            add("Customer", getattr(doc, 'customer', '')),
            add("Contact", getattr(doc, 'contact_display', '') or getattr(doc, 'contact_person', '') or ''),
            add("Delivery Address", getattr(doc, 'customer_address', '')),
            "",
            "Thank you for choosing us.",
            "",
            f"Best regards,\n{company}"
        ]
    elif doc.doctype == "Payment Entry":
        lines = [
            f"Dear {getattr(doc, 'party', party_type)},",
            "",
            f"A Payment Entry *{doc.name}* has been submitted.",
            add("Date", frappe.utils.formatdate(doc.posting_date)),
            add("Amount", frappe.utils.fmt_money(doc.paid_amount, currency=getattr(doc, 'paid_to_account_currency', None) or getattr(doc, 'party_account_currency', None) or '')),
            add("Party", getattr(doc, 'party', '')),
            add("Reference", getattr(doc, 'reference_no', '')),
            "",
            "Best regards,",
            f"{company}"
        ]
    else:
        lines = [
            f"Dear {party_type},",
            "",
            f"Your {doc.doctype.replace('_', ' ')} *{doc.name}* has been submitted.",
            "",
            f"Best regards,\n{company}"
        ]
    # Remove None, empty, or whitespace-only lines
    return "\n".join([line for line in lines if line and str(line).strip() and str(line).strip().lower() != "none"])


def send_document_whatsapp_on_submit(doc, method=None):
    """
    On submit of Sales Invoice, Purchase Invoice, Delivery Note, or Payment Entry:
    - If enabled in settings, create a WH Massage doc with message details.
    - Do not send WhatsApp message, only insert record.
    """
    settings = frappe.get_single("Wassenger Settings")

    # Map setting fieldnames to DocTypes
    doctype_settings_map = {
        "Sales Invoice": settings.send_sales_invoice_on_submit,
        "Purchase Invoice": settings.send_purchase_invoice_on_submit,
        "Delivery Note": settings.send_delivery_note_on_submit,
        "Payment Entry": settings.send_payment_entry_on_submit,
    }

    if not doctype_settings_map.get(doc.doctype):
        return  # Not enabled for this doctype

    # Determine party and WhatsApp number
    whatsapp_number = None
    party_type = None
    party_name = None
    if doc.doctype == "Sales Invoice":
        party_type = "Customer"
        party_name = doc.customer
        whatsapp_number = frappe.db.get_value("Customer", doc.customer, "mobile_no") or getattr(doc, "mobile_no", None)
    elif doc.doctype == "Purchase Invoice":
        party_type = "Supplier"
        party_name = doc.supplier
        whatsapp_number = frappe.db.get_value("Supplier", doc.supplier, "mobile_no") or getattr(doc, "mobile_no", None)
    elif doc.doctype == "Delivery Note":
        party_type = "Customer"
        party_name = doc.customer
        whatsapp_number = frappe.db.get_value("Customer", doc.customer, "mobile_no") or getattr(doc, "mobile_no", None)
    elif doc.doctype == "Payment Entry":
        party_type = doc.party_type
        party_name = doc.party
        if doc.party_type == "Customer":
            whatsapp_number = frappe.db.get_value("Customer", doc.party, "mobile_no")
        elif doc.party_type == "Supplier":
            whatsapp_number = frappe.db.get_value("Supplier", doc.party, "mobile_no")

    if not whatsapp_number:
        frappe.log_error(f"No WhatsApp number found for {party_type} in {doc.doctype} {doc.name}")
        return

    # Prepare detailed message
    message = get_professional_whatsapp_message(doc, party_type)

    # Prepare attachment if allowed
    send_file = settings.allow_send_pdf_attachment
    file_url = None
    file_name = None
    if send_file:
        try:
            file_url = frappe.utils.get_url(
                f"/api/method/frappe.utils.print_format.download_pdf?doctype={doc.doctype}&name={doc.name}&format=Standard&no_letterhead=0"
            )
            file_name = f"{doc.doctype}-{doc.name}.pdf"
        except Exception:
            file_url = None

    # --- Create WH Massage record ---
    wh_massage_doc = frappe.get_doc({
        "doctype": "WH Massage",
        "reference_doctype": doc.doctype,
        "reference_name": doc.name,
        "party_type": party_type,
        "party": party_name,
        "phone": whatsapp_number,
        "send_message": message,
        "file": file_url if (send_file and file_url) else None,
        "status": "Pending",
        "type": "out"
    })
    wh_massage_doc.insert(ignore_permissions=True)
    wh_massage_doc.reload()  
    wh_massage_doc.submit()  
    frappe.db.commit()