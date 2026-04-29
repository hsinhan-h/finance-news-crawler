import base64
import logging
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from notifier.message_builder import build_message, render_html_body

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
		with open(token_file, "w", encoding="utf-8") as f:
			f.write(creds.to_json())
	return creds


def send_via_gmail_oauth(config: dict, report_path: str, report_date: str) -> bool:
	credentials_file = config.get("credentials_file", "credentials.json")
	token_file = config.get("token_file", "token.json")
	sender = config.get("sender_address", "")
	recipients = config.get("recipients", [])
	subject_template = config.get("subject_template", "每日財經摘要 {date}")
	subject = subject_template.format(date=report_date)

	if not os.path.exists(credentials_file):
		logger.error(
			"credentials.json not found at '%s'. Please follow the setup guide in README.md.",
			credentials_file,
		)
		return False

	try:
		creds = _get_credentials(credentials_file, token_file)
		service = build("gmail", "v1", credentials=creds)
		html_body = render_html_body(report_path)
		message = build_message(sender, recipients, subject, html_body, report_path)
		raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
		service.users().messages().send(userId="me", body={"raw": raw}).execute()
		logger.info("Email sent to %s via Gmail OAuth", recipients)
		return True
	except Exception as e:
		logger.error("Failed to send email via Gmail OAuth: %s", e, exc_info=True)
		return False