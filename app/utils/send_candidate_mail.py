# app/utils/candidate_email.py

from app.utils.email_templates_utils import render_email
from app.utils.email_ses import send_email_ses  # ✅ SES instead of SMTP
from app.config import settings

def send_candidate_email(candidate, status, job_posting):
    """
    Send acceptance / rejection email to candidate using Amazon SES.
    """

    context = {
        "candidate_name": f"{candidate.first_name} {candidate.last_name}",
        "job_title": job_posting.job_description.title,
        "location": job_posting.location,
        "interview_datetime": getattr(candidate, "interview_datetime", None),
        "organization_name": settings.ORGANIZATION_NAME,
        "organization_logo": settings.ORGANIZATION_LOGO_URL
    }

    if status.lower() == "accepted":
        template = "candidate_accepted.html"
        subject = f"Congratulations — {job_posting.job_description.title}"
    else:
        template = "candidate_rejected.html"
        subject = f"Application Update — {job_posting.job_description.title}"

    html_body = render_email(template, context)

    # ✅ Use SES to send email
    send_email_ses(subject, html_body, candidate.email)
