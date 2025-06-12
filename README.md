
---
title: Wassenger Integration for Frappe/ERPNext
author: Ahmed Emam
version: 1.1
license: MIT
---

# 🚀 Wassenger Integration for Frappe/ERPNext

**Wassenger Integration** is a feature-rich Frappe application that brings seamless **WhatsApp messaging automation** to your ERPNext system. From sending invoices and delivery notes to auto-logging customer responses, this app is designed to streamline communication right from your ERP.

---

## 🚀 Key Features

- **Send WhatsApp Messages** from selected DocTypes like **Sales Invoices** and **Payment Entries**
- **PDF Attachments**: Seamlessly attach and send documents (e.g., invoices, quotations)
- **Status Tracking**: Monitor delivery and read receipts in real-time
- **Automated Reply Logging**: Replies are logged automatically in the system as inbound messages
- **Easy Configuration**: Intuitive setup via the Wassenger Settings page
- **Multi-Tenant Ready**: Designed for scalability in production environments
- **Contact Sync**: Sync WhatsApp contacts with your ERPNext Contacts/Customers/Suppliers
- **Enhanced Error Logging**: Detailed logs for failed deliveries, invalid numbers, and API errors
- **Permission Control**: Granular user permissions for sending and viewing WhatsApp messages
- **API Endpoints**: Public API endpoints for custom integrations and advanced automations
- **Webhook Signature Verification**: Secure webhook integration with signature validation for inbound events

---

## 🛠️ Requirements

- Frappe/ERPNext Version **13 or higher**
- **bench CLI** – [Install it here](https://github.com/frappe/bench)
- **Wassenger Account** with API access

---

## 📦 Installation Steps

```bash
cd /path/to/your/bench
bench get-app https://github.com/ahmedemamhatem/wassenger_integration.git 
bench install-app wassenger_integration
bench restart
```

---

## ⚙️ Configuration

### ERP Setup
- Navigate to **Wassenger Settings**
- Input your **Wassenger API Key**
- Set your **Public ERP URL** (e.g., `https://erp.yourcompany.com`)

### Wassenger Dashboard
- Copy Webhook URLs from **Wassenger Settings**
- Paste them in Wassenger dashboard under Webhooks:
  - **Status Update URL**
  - **Reply Webhook URL**
- (Optional) Enable **Signature Verification** for secure callbacks

---

## 📄 How to Use

### 🔘 Manual Messaging

1. Go to a supported DocType (e.g., `WH Message`, `Sales Invoice`, or `Payment Entry`)
2. Add the recipient’s **phone number** and compose your **message** or select a **template**
3. *(Optional)* Attach relevant **PDF documents** (e.g., invoice, receipt)
4. Click **Submit** — the system will automatically trigger **Send WhatsApp Message**

---

### ⚙️ Automated Messaging on Submit

- In **Wassenger Settings**, select the DocTypes you want to enable for **auto messaging**
- When any of these DocTypes are submitted, the system will automatically:
  - Extract the configured message/template
  - Attach any predefined PDFs (if set)
  - Send the message to the associated phone number
  - Log the sent message and update delivery/read status

> 💡 This feature is ideal for automating customer notifications on invoice creation, payment confirmation, and more.

---

## 🔄 Automation and Logs

- Replies are auto-logged as **Inbound Messages**
- Status (Sent / Delivered / Read / Failed) is tracked automatically
- Failed messages are saved with **detailed error descriptions**

---

## 🔁 Contact Sync

- Automatically sync WhatsApp numbers with ERPNext:
  - **Contacts**
  - **Customers**
  - **Suppliers**


---

## 🔌 API Endpoints

- Send WhatsApp message
- Get message status
- Fetch message logs and Replays

See the `/api/` directory and [Wassenger API Docs](https://wassenger.com/docs/) for full details.

---

## 📚 References

- [Frappe Framework Docs](https://frappeframework.com/docs)
- [Wassenger API Documentation](https://wassenger.com/docs/)
- See `/docs/` directory for advanced use cases and samples

---

## 📝 License

This app is licensed under the **MIT License**.  
Crafted with ❤️ by **Ahmed Emam**
