# Laptop Asset QR

- data: `docs/data.json`
- generated pages: `docs/assets/*.html`
- generated QR: `docs/qrcodes/*.png`

## Run locally
python -m http.server 8000  (from docs/)
open http://localhost:8000

## Generate
pip install -r requirements.txt
python generate.py
