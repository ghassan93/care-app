import logging
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

@shared_task
def send_marketing_email_task(subject, recipient_list, context, template_name,):
    logger.info("Task started: Preparing to send email...")
    try:
        logger.info(f"Recipient list: {recipient_list}")
        email_html_message = render_to_string(template_name, context)
        logger.info("Email template rendered successfully.")
        email = EmailMessage(
            subject=subject,
            body=email_html_message,
            from_email="info@care-app.live",
            to=recipient_list,
        )
        email.content_subtype = "html"
        email.send()
        logger.info(f"Email sent to {', '.join(recipient_list)}")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise
