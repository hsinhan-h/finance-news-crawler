import mimetypes
import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import markdown2


def render_html_body(report_path: str) -> str:
	with open(report_path, "r", encoding="utf-8") as f:
		md_content = f.read()
	return markdown2.markdown(md_content, extras=["tables", "fenced-code-blocks"])


def build_message(
	sender: str,
	recipients: list[str],
	subject: str,
	html_body: str,
	attachment_path: str,
) -> MIMEMultipart:
	msg = MIMEMultipart("mixed")
	msg["From"] = sender
	msg["To"] = ", ".join(recipients)
	msg["Subject"] = subject

	msg.attach(MIMEText(html_body, "html", "utf-8"))

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

	return msg