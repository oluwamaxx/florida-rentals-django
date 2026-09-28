from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape
from .models import SMTPSettings


def send_tour_notification(tour):
    smtp = SMTPSettings.get_solo()
    if not (smtp.enabled and smtp.host and smtp.notification_email):
        return False, 'SMTP notifications are disabled or incomplete.'
    from django.conf import settings
    from django.core import mail
    connection = mail.get_connection(
        backend='django.core.mail.backends.smtp.EmailBackend',
        host=smtp.host, port=smtp.port, username=smtp.username or None,
        password=smtp.password or None, use_tls=smtp.use_tls, use_ssl=smtp.use_ssl,
        fail_silently=False,
    )
    from_email = smtp.from_email or smtp.username or settings.DEFAULT_FROM_EMAIL
    subject = f'New Schedule Self Tour request — {tour.listing.title}'
    lines = [
        f'Property: {tour.listing.title}', f'Address: {tour.listing.full_address}',
        f'Name: {tour.name}', f'Phone: {tour.phone}',
        f'Monthly gross income: ${tour.monthly_gross_income:,.2f}',
        f'Evicted before: {"Yes" if tour.has_been_evicted else "No"}',
        f'Years renting: {tour.years_renting:g}', f'Move-in date: {tour.move_in_date:%B %d, %Y}',
        f'Reason for moving: {tour.reason_for_moving}',
        f'Funds available to secure house: ${tour.funds_to_secure:,.2f}',
        f'Submitted: {tour.created_at:%Y-%m-%d %H:%M %Z}',
    ]
    msg = EmailMultiAlternatives(subject, '\n'.join(lines), from_email, [smtp.notification_email], connection=connection)
    msg.send(fail_silently=False)
    return True, ''
