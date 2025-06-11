# Wassenger Integration

**Wassenger Integration** is a Frappe app that brings full WhatsApp messaging automation to your ERPNext or Frappe system.  
Send messages (with or without PDF attachments), track delivery status, and receive replies—all from within your ERP workflow.

---

## 🚀 Features

- **Send WhatsApp messages** from any Frappe doctype  
- **Attach and send PDFs** (e.g. invoices, quotes) via WhatsApp  
- **Track delivery and read status** on sent messages  
- **Automatically log WhatsApp replies** as inbound messages  
- **User-friendly setup** via the Wassenger Settings page  
- **Multi-tenant & production-ready**  

---

## 🛠️ Installation

### Requirements

- Frappe/ERPNext v13+  
- [bench CLI](https://github.com/frappe/bench)  
- [Wassenger](https://wassenger.com/) account with API access  

### To install:

```shell
cd /path/to/your/bench
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app wassenger_integration
```

---

## ⚙️ Configuration

### Set up your API Key & ERP URL

1. Go to **Wassenger Settings** in your ERP  
2. Enter your **Wassenger API Key**  
3. Enter your **public ERP URL** (e.g. `https://erp.yourcompany.com`)  

### Set up Webhooks in Wassenger

1. Copy the **Status Update** and **Reply Webhook URLs** from Wassenger Settings  
2. Paste them into your Wassenger dashboard under **Webhooks**

---

## 📦 Usage

1. Go to any supported DocType (e.g. `WH Massage`)  
2. Enter the recipient **phone number** and your **message**  
3. *(Optional)* Attach a **PDF document**  
4. Click the **Send WhatsApp Message** button  

---

## 🔁 Receiving Replies & Status

- Incoming WhatsApp **replies** are logged as `"inbound"` records  
- Message **status** will auto-update as Wassenger delivers and reads the message  

---

## 🧑‍💻 Contributing

We use **pre-commit** to check formatting and enforce code quality.

### Install pre-commit:

```shell
pip install pre-commit
```

### Enable it in your repo:

```shell
cd apps/wassenger_integration
pre-commit install
```

### Pre-commit hooks include:

- `ruff` (Python)  
- `eslint` (JavaScript)  
- `prettier` (JS/CSS/HTML)  
- `pyupgrade` (Python syntax)  

### Run all hooks:

```shell
pre-commit run --all-files
```

---

## 📚 Documentation

- [Wassenger API Reference](https://wassenger.com/docs)
- [Frappe Framework Docs](https://frappeframework.com/docs)
- See `docs/` directory for more usage and developer notes.

---

## 📝 License

This app is licensed under the **MIT License**.
