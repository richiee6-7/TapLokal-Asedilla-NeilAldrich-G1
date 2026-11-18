# TapLokal – Web-Based Civic Ticketing and Localized Emergency Alerts

CSIT327-G1 · Django (templates) + PostgreSQL/Supabase

## Features
**Standard features (Project Development 1):** registration, login/logout,
role-based dashboards (Resident / Staff), and user profile.

**Core feature (Project Development 2): Hazard Reporting**
Residents report a barangay hazard (flood, downed wires, uncollected trash, …) by choosing
a hazard type, pinning the location on a map, entering the street address and description,
and optionally uploading a photo. They can search/filter their reports, watch each report's
status timeline, and edit or delete a report while it is still *Pending*.
Staff manage the reports and hazard types (see the staff section below once merged).

Business rules implemented: only logged-in residents can file reports; each report is linked
to its author; residents only see and change their own reports; edit/delete only while
Pending (BR-11); every status is logged with who and when (BR-17); latitude/longitude and
status are enforced by CHECK constraints (BR-07, BR-08, BR-09); inactive hazard types cannot
be chosen for new reports (BR-10).

## Structure
- `taplokal/` – settings and root URLs
- `accounts/` – custom user, registration, login/logout, profile
- `dashboard/` – role dashboards and the custom admin panel (Django admin is not used)
- `reports/` – hazard types, hazard reports, status history
- `templates/` – `registration/`, `includes/`, `dashboard/`, `reports/`, base layout

## Setup
```bash
python -m venv venv
venv\Scripts\activate            # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env             # fill in your PostgreSQL / Supabase credentials
python manage.py migrate         # also seeds the default hazard types
python manage.py createsuperuser # first staff account (superusers are STAFF)
python manage.py runserver
```
Residents sign up at `/accounts/signup/`. Uploaded photos are saved in `media/` (not committed).
