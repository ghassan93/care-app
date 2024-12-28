import base64
import os
import pdfkit
from django.conf import settings
from django.template.loader import render_to_string
from authapp import tasks as auth_task

OPTIONS = {
    'page-size': 'A4', 'margin-top': '0in', 'margin-right': '0in',
    'margin-bottom': '0in', 'margin-left': '0in', 'encoding': "UTF-8",
    'no-outline': None
}

BASE_STATIC = settings.STATICFILES_DIRS[0]

SUBJECT = 'care/authapp/email/email-notify-subject.txt'
TEMPLATE = 'care/authapp/email/email-notify-message.html'

QR_MESSAGE_FORMAT = "{name}{vat}{date} {time}{total}{tax}"


def send_email(user, subject, message, **kwargs):
    """
    This function is used to send email notifications containing a special
    code that the user uses to activate something
    like send reset password or activate email.
    """

    ctx = {
        'name': user.get_full_name(),
        'subject': subject,
        'message': message,
    }
    auth_task.send_mail_task.delay(SUBJECT, TEMPLATE, ctx, user.email, **kwargs)


def render_pdf_file_from_html(template_name, css_file, context):
    """
    this function is used to generate pdf file from html
    template
    @return: pdf file
    """

    html = render_to_string(template_name, context)
    return pdfkit.from_string(html, False, OPTIONS, css=css_file)


def render_invoice_pdf(invoice):
    """
    this function is used to generate pdf file from html
    template
    @return: pdf file
    """

    ctx = {
        'invoice': invoice,
        'data': get_qr_code(invoice)
    }

    template = 'care/authapp/email/email-notify-invoice-message.html'
    css_file = [
        os.path.join(BASE_STATIC, 'care/assets/css/bootstrap.css'),
        os.path.join(BASE_STATIC, 'care/assets/css/app-rtl.css')
    ]
    return render_pdf_file_from_html(template, css_file, ctx)


def get_qr_code(invoice):
    """
    this func used to return qr data from items
    @param invoice: the invoice instance
    @return: str
    """
    invoice_date = invoice.created_date.date()
    invoice_time = invoice.created_date.time().strftime('%H:%M:%S')

    qr_code = QR_MESSAGE_FORMAT.format(
        name=settings.CARE_COMPANY_NAME, vat=settings.CARE_VAT_NUMBER,
        date=invoice_date, time=invoice_time,
        total=invoice.get_total_value, tax=invoice.get_tax_value
    )

    return base64.b64encode(qr_code.encode('utf-8')).decode('utf-8')


def get_correct_discount_value(discount_value):
    """
    this function is used to return correct discount value for care system
    @param discount_value: the old discount value
    @return: correct discount value
    """
    max_discount_value = settings.CARE_DEFAULT_DISCOUNT_VALUE
    return max_discount_value if discount_value > max_discount_value else discount_value


def get_back_cash_value(total_paid):
    """
    This function is used to return (back cash) value from total_paid
    @param total_paid: This variable denotes the value paid
    @return: back cash value
    """

    return total_paid * settings.CARE_BACK_CASH_VALUE
