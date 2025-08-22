# COD-Only Food Ordering App (Swiggy-like)

A minimal Swiggy-style food ordering web app supporting **Cash on Delivery only**.

## Features
- Browse restaurants and menus
- Add to cart, update quantities, remove items
- Checkout with name, phone, address (COD only)
- Order confirmation page with order id
- Simple admin page to list orders (password protected)
- SQLite-less JSON storage for demo (no separate DB setup required)

## Tech
- Python 3.10+
- Flask (Jinja templates, sessions)
- Vanilla JS + Fetch + Bootstrap styles (CDN)

## Quick Start
```bash
# 1) Create & activate a virtual env (recommended)
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Run
export FLASK_ENV=development           # Windows (PowerShell):  $env:FLASK_ENV="development"
export SECRET_KEY="change-me-please"   # Windows: $env:SECRET_KEY="change-me-please"
export ADMIN_PASSWORD="admin123"       # Windows: $env:ADMIN_PASSWORD="admin123"
python app.py

# App will start on http://127.0.0.1:5000
```

## Admin
Visit `/admin/orders` and enter the admin password (env var `ADMIN_PASSWORD`).

## Data Persistence
Orders are appended to `data/orders.json`. Sample restaurants & menus come from `data/seed.json`.
You can edit these files to customize your app.

## Notes
- This is a demo project: no payment gateway, only **Cash on Delivery**.
- Do **not** expose admin password publicly.
- For production, use a real DB and proper auth.
