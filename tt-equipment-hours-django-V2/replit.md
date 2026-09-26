# TT Equipment Hours

A server-rendered Django app for recording cumulative operating hours for TT01–TT18 equipment.

## Run & Operate

- `.venv/bin/python manage.py runserver 0.0.0.0:8000` — run the Django app
- `.venv/bin/python manage.py check` — run Django system checks
- `.venv/bin/python manage.py test` — run Django tests
- `.venv/bin/python manage.py migrate` — apply SQLite migrations
- `.venv/bin/python manage.py seed_equipment` — ensure TT01–TT18 exist

## Stack

- Python 3.13 and Django 6.1
- SQLite3
- Django Templates, HTML, CSS, and small vanilla JavaScript
- openpyxl for `.xlsx` export

## Where things live

- `tt_hours/` — Django project settings and URL configuration
- `equipment/` — models, service validation, forms, views, templates, static assets, admin, migrations, and tests
- `manage.py` — Django management entry point
- `db.sqlite3` — local development database, created by migrations

## Architecture decisions

- Cumulative readings are validated on the backend with `Decimal`: latest reading ≤ new reading ≤ latest reading + 8.
- Each save runs inside `transaction.atomic()` and locks the selected equipment row before re-checking the latest reading.
- Equipment with no history must have an Admin-configured initial reading; the app never silently assumes zero.
- Reporting and Excel export are staff-only; operators use the public entry form.

## Product

Operators enter cumulative readings for an operator/equipment pair. Staff users can filter records, export Excel, and manage operators, equipment, and records in Django Admin.

## User preferences

- Use Django templates and plain HTML/CSS/vanilla JavaScript only; do not introduce React, Vue, Angular, or frontend frameworks.

## Gotchas

- Run `migrate` before `seed_equipment`.
- Configure each equipment's Initial cumulative hours in Admin before its first entry.

## Pointers

- See `README.md` for local setup and URLs.
