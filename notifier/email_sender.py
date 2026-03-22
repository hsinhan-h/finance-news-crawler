"""
Gmail OAuth 2.0 email sender.
Only activated when config.yaml has email.enabled: true.
"""
import base64
import logging
import mimetypes
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import markdown2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def _get_credentials(credentials_file: str, token_file: str) -> Credentials:
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return creds


def _build_message(
    sender: str,
    recipients: list[str],
    subject: str,
    html_body: str,
    attachment_path: str,
) -> dict:
    msg = MIMEMultipart("mixed")
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    # HTML body
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # Attach the .md file
    if attachment_path and os.path.exists(attachment_path):
        ctype, encoding = mimetypes.guess_type(attachment_path)
        if ctype is None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(attachment_path, "rb") as f:
            part = MIMEBase(maintype, subtype)
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            "attachment",
            filename=os.path.basename(attachment_path),
        )
        msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


def send_report(config: dict, report_path: str, report_date: str) -> bool:
    """
    Send the report via Gmail OAuth.
    Returns True on success, False on failure.
    config is the email sub-dict from config.yaml.
    """
    credentials_file = config.get("credentials_file", "credentials.json")
    token_file = config.get("token_file", "token.json")
    sender = config.get("sender_address", "")
    recipients = config.get("recipients", [])
    subject_template = config.get("subject_template", "每日財經摘要 {date}")
    subject = subject_template.format(date=report_date)

    if not os.path.exists(credentials_file):
        logger.error(f"credentials.json not found at '{credentials_file}'. Please follow the setup guide in README.md.")
        return False

    try:
        creds = _get_credentials(credentials_file, token_file)
        service = build("gmail", "v1", credentials=creds)

        with open(report_path, "r", encoding="utf-8") as f:
            md_content = f.read()
        html_body = markdown2.markdown(md_content, extras=["tables", "fenced-code-blocks"])

        message = _build_message(sender, recipients, subject, html_body, report_path)
        service.users().messages().send(userId="me", body=message).execute()
        logger.info(f"Email sent to {recipients}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}", exc_info=True)
        return False
