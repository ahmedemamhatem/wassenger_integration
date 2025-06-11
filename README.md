---
title: Wassenger Integration for Frappe/ERPNext
author: Ahmed Emam
version: 1.0
license: MIT
---

# Wassenger Integration

**Wassenger Integration** is a powerful Frappe application designed to automate WhatsApp messaging workflows directly from your ERPNext system. It simplifies communication by enabling message sending, delivery tracking, and automated logging of responses—all within your existing ERP processes.

---

## 🚀 Key Features

- **WhatsApp Messaging from Frappe**: Send messages directly from any DocType.
- **PDF Attachments**: Seamlessly attach and send documents (e.g., invoices, quotations).
- **Status Tracking**: Monitor delivery and read receipts in real-time.
- **Automated Reply Logging**: Replies are logged automatically in the system as inbound messages.
- **Easy Configuration**: Intuitive setup via the Wassenger Settings page.
- **Multi-Tenant Ready**: Designed for scalability in production environments.

---

## 🛠️ System Requirements

- **Frappe/ERPNext**: Version 13 or higher
- **bench CLI**: [Install from GitHub](https://github.com/frappe/bench)
- **Wassenger Account**: With API access enabled

---

## 📦 Installation Guide

1. Navigate to your bench directory:
    ```bash
    cd /path/to/your/bench
    ```

2. Get the app:
    ```bash
    bench get-app https://github.com/ahmedemamhatem/wassenger_integration.git --branch develop
    ```

3. Install the app:
    ```bash
    bench install-app wassenger_integration
    ```

4. Restart your bench:
    ```bash
    bench restart
    ```

---

## ⚙️ Configuration Steps

### Step 1: ERP Setup

- Go to **Wassenger Settings** in your ERP
- Enter your **Wassenger API Key**
- Provide your **ERP Public URL** (e.g., `https://erp.yourcompany.com`)

### Step 2: Configure Webhooks on Wassenger

- Copy the **Status Update** and **Reply Webhook URLs** from Wassenger Settings
- Paste them into the **Webhooks** section in your Wassenger dashboard

---

## 📄 Usage Instructions

1. Navigate to a supported DocType (e.g., `WH Message`)
2. Enter the recipient's **phone number** and compose your **message**
3. *(Optional)* Attach a **PDF document**
4. Click **Send WhatsApp Message**

---

## 🔁 Automatic Logging and Status Updates

- **Inbound Replies**: Logged as new documents under the designated inbound DocType
- **Delivery Tracking**: Message status automatically updates based on Wassenger delivery/read receipts

---

## 🧑‍💻 Developer Guide

We enforce coding standards and quality using **pre-commit hooks**.

### Install pre-commit:

```bash
pip install pre-commit
```

### Enable it in your repo:

```bash
cd apps/wassenger_integration
pre-commit install
```

### Hooks Used:

- `ruff` - Python linting
- `eslint` - JavaScript linting
- `prettier` - Code formatting (JS/CSS/HTML)
- `pyupgrade` - Ensures modern Python syntax

### Run all checks:

```bash
pre-commit run --all-files
```

---

## 📚 Resources & References

- [Wassenger API Docs](https://wassenger.com/docs)
- [Frappe Framework Documentation](https://frappeframework.com/docs)
- Additional usage examples and developer notes in the `docs/` directory.

---

## 📝 License

This project is released under the **MIT License**. You are free to use, modify, and distribute it as per the license terms.

---

*Crafted with ❤️ by the ERPNext Developer Team*
