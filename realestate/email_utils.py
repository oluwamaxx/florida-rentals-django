import os
import resend

from .models import SMTPSettings


def send_tour_notification(tour):
    smtp = SMTPSettings.get_solo()

    if not (smtp.enabled and smtp.notification_email):
        return False, "Email notifications are disabled or incomplete."

    api_key = os.environ.get("RESEND_API_KEY")

    if not api_key:
        return False, "RESEND_API_KEY is not configured."

    subject = f"New Schedule Self Tour request - {tour.listing.title}"

    lines = [
        f"Property: {tour.listing.title}",
        f"Address: {tour.listing.full_address}",
        f"Name: {tour.name}",
        f"Phone: {tour.phone}",
        f"Monthly gross income: ${tour.monthly_gross_income:,.2f}",
        f"Evicted before: {'Yes' if tour.has_been_evicted else 'No'}",
        f"Years renting: {tour.years_renting}",
        f"Move-in date: {tour.move_in_date:%B %d, %Y}",
        f"Reason for moving: {tour.reason_for_moving}",
        f"Funds available to secure house: ${tour.funds_to_secure:,.2f}",
        f"Submitted: {tour.created_at:%Y-%m-%d %H:%M %Z}",
    ]

    resend.api_key = api_key

    params = {
        "from": "onboarding@resend.dev",
        "to": [smtp.notification_email],
        "subject": subject,
        "text": "\n".join(lines),
    }

    try:
        resend.Emails.send(params)
    except Exception as exc:
        return False, f"Resend email failed: {exc}"

    return True, ""