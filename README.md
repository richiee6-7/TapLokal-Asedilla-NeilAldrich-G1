# TapLokal – Web-Based Civic Ticketing and Localized Emergency Alerts

CSIT327-G1 · Phase 1: Account Feature (Django templates + PostgreSQL/Supabase)

## Structure
- `taplokal/` – project settings and root URLs
- `accounts/` – custom user model, registration, login/logout, profile
- `dashboard/` – role-based dashboards and the custom admin panel (Django admin is not used)
- `templates/` – base, `registration/`, `includes/`, `dashboard/`, `profile.html`

## Setup
```bash
python -m venv venv
venv\Scripts\activate            # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env             # fill in your PostgreSQL / Supabase credentials
python manage.py migrate
python manage.py createsuperuser # first staff account (superusers are STAFF)
python manage.py runserver
```
Residents sign up at `/accounts/signup/`. Staff can add more staff accounts and manage
users from the Admin Panel (`/admin-panel/`).
