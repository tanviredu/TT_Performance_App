# TT Equipment Hours

A lightweight Django application for recording cumulative TT equipment hour-meter readings.

## Requirements

- Python 3.11+
- SQLite3

## Install

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations and seed the fixed equipment list:

```bash
python manage.py migrate
python manage.py seed_equipment
```

The initial migration creates TT01 through TT18 and OP001 through OP005. Add, rename, activate, or deactivate operators in Django Admin.

Create an administrator:

```bash
python manage.py createsuperuser
```

Run the server:

```bash
python manage.py runserver
```

Open:

- Entry form: `http://127.0.0.1:8000/`
- Staff report: `http://127.0.0.1:8000/reports/`
- Django Admin: `http://127.0.0.1:8000/admin/`

Before the first entry for each equipment, set its **Initial cumulative hours** in Admin. Each new reading must be between the latest stored reading and that reading plus 8 hours. Validation is enforced on the Django backend with decimal arithmetic and an atomic save.