import json
from pathlib import Path
from string import Template

import qrcode  # pip install qrcode[pil]

BASE = Path(__file__).parent
DOCS = BASE / "docs"
ASSETS_DIR = DOCS / "assets"
QRCODES_DIR = DOCS / "qrcodes"
DATA_PATH = DOCS / "data.json"

ASSETS_DIR.mkdir(parents=True, exist_ok=True)
QRCODES_DIR.mkdir(parents=True, exist_ok=True)

HTML_TEMPLATE = Template(r"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>$ASSET_ID | OMIDAR Asset</title>
  <style>
    :root {
      --bg:#0b0f14; --card:#121824; --text:#e9eef6; --muted:#a9b4c4; --line:rgba(255,255,255,.08);
      --accent:#6bb56b;
    }
    body {
      margin:0; font-family:system-ui,-apple-system,"Segoe UI",Tahoma,Arial,sans-serif;
      background: radial-gradient(1200px 600px at 70% -10%, rgba(107,181,107,.18), transparent 60%),
                  radial-gradient(900px 500px at 10% 10%, rgba(255,255,255,.06), transparent 55%),
                  var(--bg);
      color:var(--text);
    }
    .wrap { max-width:900px; margin:0 auto; padding:28px 16px 48px; }
    .header {
      display:flex; gap:14px; align-items:center; justify-content:space-between; flex-wrap:wrap;
      border:1px solid var(--line); background:rgba(18,24,36,.75); border-radius:18px; padding:14px 16px;
      backdrop-filter: blur(8px);
    }
    .brand { display:flex; gap:12px; align-items:center; }
    .brand img { width:56px; height:56px; border-radius:14px; object-fit:cover; border:1px solid var(--line); background:#fff; }
    .chip {
      border:1px solid rgba(107,181,107,.35);
      background:rgba(107,181,107,.12);
      color:#cfeecf; padding:6px 10px; border-radius:999px; font-size:12px;
    }
    .grid { margin-top:14px; display:grid; grid-template-columns: 1.2fr .8fr; gap:14px; }
    @media (max-width:860px){ .grid{ grid-template-columns:1fr; } }
    .card { border:1px solid var(--line); background:rgba(18,24,36,.75); border-radius:18px; padding:16px; }
    .kv { display:grid; grid-template-columns:170px 1fr; gap:8px 12px; margin-top:10px; padding-top:12px; border-top:1px dashed rgba(255,255,255,.1); }
    .k { color:var(--muted); font-size:13px; }
    .v { font-size:14px; line-height:1.5; }
    .actions { display:flex; gap:10px; flex-wrap:wrap; margin-top:12px; }
    button,a.btn {
      cursor:pointer; border:1px solid var(--line); background:rgba(255,255,255,.04);
      color:var(--text); padding:10px 12px; border-radius:12px; font-size:13px; text-decoration:none;
    }
    button:hover,a.btn:hover { border-color: rgba(107,181,107,.35); }
    .qr img { width:180px; height:180px; border-radius:14px; background:#fff; padding:8px; }
    code { background:rgba(255,255,255,.06); padding:2px 6px; border-radius:8px; }
    .note { margin-top:12px; color:var(--muted); font-size:12px; line-height:1.7; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <div class="brand">
        <img src="../img/omidar.jpg" alt="logo">
        <div>
          <div style="font-weight:800;">OMIDAR | بيانات جهاز</div>
          <div style="color:var(--muted);font-size:13px;">Asset ID: <code id="aid">$ASSET_ID</code></div>
          <div style="color:var(--muted);font-size:13px;">username: <code>$USERNAME</code></div>
        </div>
      </div>
      <div class="chip">$STATUS</div>
    </div>

    <div class="grid">
      <div class="card">
        <div style="font-weight:800;">المواصفات</div>
        <div class="kv">
          <div class="k">اسم الموظف</div><div class="v">$EMPLOYEE_NAME</div>
          <div class="k">الشركة</div><div class="v">$COMPANY</div>
          <div class="k">النوع / الموديل</div><div class="v">$BRAND — $MODEL</div>
          <div class="k">CPU</div><div class="v">$CPU</div>
          <div class="k">Screen</div><div class="v">$SCREEN</div>
          <div class="k">RAM</div><div class="v">$RAM</div>
          <div class="k">Storage</div><div class="v">$STORAGE</div>
          <div class="k">Serial</div><div class="v">$SERIAL</div>
          <div class="k">Delivery Date</div><div class="v">$DELIVERY_DATE</div>
          <div class="k">Notes</div><div class="v">$NOTES</div>
        </div>

        <div class="actions">
          <button onclick="copyText('$ASSET_ID')">نسخ Asset ID</button>
          <a class="btn" href="../index.html">رجوع للقائمة</a>
        </div>

        <div class="note">
          ⚠️ لا تضع كلمات مرور داخل QR أو GitHub. استخدم Asset ID مع Password Manager.
        </div>
      </div>

      <div class="card qr">
        <div style="font-weight:800;margin-bottom:10px;">QR Code</div>
        <div style="color:var(--muted);font-size:13px;margin-bottom:10px;">
          الرابط: <code id="u">$URL</code>
        </div>
        <img src="../qrcodes/$ASSET_ID.png" alt="QR">
        <div class="actions" style="margin-top:12px;">
          <button onclick="copyText(document.getElementById('u').innerText)">نسخ الرابط</button>
        </div>
      </div>
    </div>
  </div>

<script>
  function copyText(t){
    navigator.clipboard.writeText(t)
      .then(() => alert("تم النسخ ✅"))
      .catch(() => prompt("انسخ يدويًا:", t));
  }
</script>
</body>
</html>
""")

def val(item, key, default="—"):
    v = item.get(key, "")
    return v if str(v).strip() else default

def main():
    gh_username = input("GitHub username: ").strip()
    repo_name = input("Repo name (laptop-asset-qr): ").strip() or "laptop-asset-qr"

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    for item in data:
        asset_id = val(item, "asset_id", "").strip()
        if not asset_id:
            continue

        url = f"https://{gh_username}.github.io/{repo_name}/assets/{asset_id}.html"

        # QR
        img = qrcode.make(url)
        img.save(QRCODES_DIR / f"{asset_id}.png")

        # HTML
        html = HTML_TEMPLATE.substitute(
            ASSET_ID=asset_id,
            URL=url,
            EMPLOYEE_NAME=val(item, "employee_name"),
            USERNAME=val(item, "username"),
            COMPANY=val(item, "company"),
            BRAND=val(item, "brand"),
            MODEL=val(item, "model"),
            CPU=val(item, "cpu"),
            SCREEN=val(item, "screen"),
            RAM=val(item, "ram"),
            STORAGE=val(item, "storage"),
            SERIAL=val(item, "serial"),
            DELIVERY_DATE=val(item, "delivery_date"),
            STATUS=val(item, "status"),
            NOTES=val(item, "notes"),
        )
        (ASSETS_DIR / f"{asset_id}.html").write_text(html, encoding="utf-8")
        print(f"✅ Generated: {asset_id}")

    print("\nDone ✅")

if __name__ == "__main__":
    main()
