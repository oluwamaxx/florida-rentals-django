# Florida Rental Listings — Django

A professional green/black Django rental website with admin-managed listings, up to 20 photos per property, ordered/main photos, dynamic home details and monthly fees, working search, connected listing/map results, Schedule Self Tour forms, editable company/contact settings, and editable SMTP notifications.

## 1. Open the project
Open this folder in VS Code and open Command Prompt/Terminal in the project folder.

## 2. Create a virtual environment
Windows CMD:
```
py -m venv venv
venv\Scripts\activate
```

## 3. Install packages
```
pip install -r requirements.txt
```

## 4. Run migrations
```
python manage.py migrate
```

## 5. Create the admin account
```
python manage.py createsuperuser
```
Follow the prompts. Then:
```
python manage.py runserver
```
Open `http://127.0.0.1:8000/` and admin at `http://127.0.0.1:8000/admin/`.

## 6. Admin setup order
1. Website Settings — set the editable company name, optional footer phone/email/address, hero text/image, and self-tour phone.
2. SMTP Email Settings — enter SMTP details, notification email, enable it, then use the admin test action.
3. Listings — add rent, bedrooms, bathrooms (decimals such as 1.5 are supported), square feet, address, status and description.
4. Upload up to 20 listing photos directly from the device. The first photo is the main photo; the inline photo rows include an order number and can be dragged to reorder. Image URL is optional.
5. Add any number of Home Details/features and Monthly Fees per listing.

## Map behavior
The Map page and homepage map request the same filtered listing data used by the search results. Listings with latitude/longitude entered in admin map immediately; if coordinates are blank, the browser makes a best-effort address lookup using OpenStreetMap Nominatim. A custom map URL is optional and is used for the individual property's Google Maps link.

For a production site, use a dedicated geocoding/maps provider and API key rather than relying on public Nominatim for heavy traffic.

## Important production steps
- Change `DJANGO_SECRET_KEY` and set `DJANGO_DEBUG=0`.
- Set `DJANGO_ALLOWED_HOSTS` to your real domain.
- Use HTTPS.
- Do not use the default SQLite database for high-traffic production; PostgreSQL is recommended.
- Protect the Django admin with a strong password and, ideally, additional security controls.
- SMTP passwords are stored in the admin database in this starter project for simplicity; for production, use environment variables or encrypted secret storage.
- Configure proper static/media hosting for production.
