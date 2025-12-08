from app.utils.email_ses import send_email_ses
from app.utils.email_templates_utils import render_email


def send_template_email(to: list, subject: str, template_name: str, context: dict):
    html_body = render_email(template_name, context)

    for email in to:
        send_email_ses(subject, html_body, email)


# ALIAS (IMPORTANT)
def send_email(to: list, subject: str, html_body: str):
    """
    Kept only for backward compatibility.
    Older routes use send_email(), so we alias it here.
    """
    for email in to:
        send_email_ses(subject, html_body, email)
