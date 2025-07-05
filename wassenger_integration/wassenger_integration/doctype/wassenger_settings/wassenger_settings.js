frappe.ui.form.on('Wassenger Settings', {
  refresh(frm) {
    // Always use the ERP URL field, never the local origin
    let erp_url = (frm.doc.erp_url || '').trim().replace(/\/$/, '');
    if(!erp_url) {
      erp_url = "https://erp.url"; // fallback placeholder for visual clarity
    }
    const webhook_status = `${erp_url}/api/method/wassenger_integration.api.whatsapp_status_update`;
    const webhook_reply = `${erp_url}/api/method/wassenger_integration.api.whatsapp_reply`;

    const html = `
      <style>
        .wassenger-info-box {
          background: #f7fafc;
          border: 1px solid #e1e4e8;
          border-radius: 8px;
          padding: 18px 18px 12px 18px;
          margin: 0 -18px 18px -18px;
          width: calc(100% + 36px);
          box-sizing: border-box;
        }
        .wassenger-webhook-row {
          display: flex;
          align-items: center;
          margin-bottom: 12px;
          flex-wrap: wrap;
        }
        .wassenger-webhook-label {
          min-width: 120px;
          font-weight: 600;
          margin-right: 8px;
        }
        .wassenger-webhook-url {
          font-family: monospace;
          background: #fff;
          border: 1px solid #ddd;
          border-radius: 4px;
          padding: 5px 8px;
          word-break: break-all;
          font-size: 12px;
          margin-right: 8px;
          flex: 1 1 220px;
        }
        .wassenger-copy-btn {
          background: #f0f4f8;
          border: 1px solid #bbb;
          border-radius: 4px;
          cursor: pointer;
          font-size: 13px;
          padding: 2px 10px;
          transition: background .18s;
        }
        .wassenger-copy-btn:hover {
          background: #e3e8ef;
        }
        @media (max-width: 600px) {
          .wassenger-info-box { padding: 10px 2px 2px 2px; margin: 0 -2vw 10px -2vw; width: 100vw; }
          .wassenger-webhook-row { flex-direction: column; align-items: stretch; }
          .wassenger-webhook-label { margin-bottom: 4px; }
          .wassenger-webhook-url { margin-right: 0; margin-bottom: 4px; }
        }
      </style>
      <div class="wassenger-info-box">
        <div style="font-size: 1.25em; margin-bottom: 10px;">
          <span style="color:#25d366; vertical-align:middle;">&#128241;</span>
          <b>Wassenger Integration for Frappe</b>
        </div>
        <div style="margin-bottom: 8px;">
          This app lets you send WhatsApp messages and documents from Frappe using Wassenger.<br>
          <ul>
            <li>Send text or PDF attachments from your forms</li>
            <li>Track sent message status</li>
            <li>Receive and log replies</li>
          </ul>
        </div>
        <hr>
        <div style="font-weight:600; margin-bottom: 10px;">
          <span style="color:#2c5282;">&#128279;</span>
          Webhook URLs (Paste these in Wassenger):
        </div>
        <div class="wassenger-webhook-row">
          <span class="wassenger-webhook-label">&#128221; Status Update:</span>
          <span class="wassenger-webhook-url" id="wassenger-status-url">
            ${webhook_status}
          </span>
          <button class="wassenger-copy-btn" type="button" onclick="navigator.clipboard.writeText('${webhook_status}');frappe.show_alert({message: 'Copied!',indicator:'green'})">&#128203; Copy</button>
        </div>
        <div class="wassenger-webhook-row">
          <span class="wassenger-webhook-label">&#128172; Reply Webhook:</span>
          <span class="wassenger-webhook-url" id="wassenger-reply-url">
            ${webhook_reply}
          </span>
          <button class="wassenger-copy-btn" type="button" onclick="navigator.clipboard.writeText('${webhook_reply}');frappe.show_alert({message: 'Copied!',indicator:'green'})">&#128203; Copy</button>
        </div>
        <div style="margin-top:12px;font-size:13px;color:#555;">
          <span style="color:#3182ce;">&#8505;</span>
          <em>
            Copy and paste these URLs as <b>Status Update</b> and <b>Reply</b> webhooks in your Wassenger dashboard.<br>
            <b>Tip:</b> If your ERP URL changes, update the <b>ERP URL</b> field above and reload to get fresh links.
          </em>
        </div>
      </div>
    `;

    frm.fields_dict.info_html.$wrapper.html(html);
  }
});