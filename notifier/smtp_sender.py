import logging
import smtplib
import ssl

from notifier.message_builder import build_message, render_html_body

logger = logging.getLogger(__name__)


def send_via_smtp(config: dict, report_path: str, report_date: str) -> bool:
	host = config.get("host", "")
	port = int(config.get("port", 587))
	security = str(config.get("security", "starttls")).lower()
	enable_smtp_auth = bool(config.get("enable_smtp_auth", True))
	login_id = config.get("login_id") or config.get("username", "")
	password = config.get("password", "")
	sender = config.get("sender_address", login_id)
	recipients = config.get("recipients", [])
	subject_template = config.get("subject_template", "每日財經摘要 {date}")
	subject = subject_template.format(date=report_date)

	try:
		html_body = render_html_body(report_path)
		message = build_message(sender, recipients, subject, html_body, report_path)

		if security == "ssl":
			context = ssl.create_default_context()
			with smtplib.SMTP_SSL(host, port, context=context, timeout=30) as server:
				if enable_smtp_auth and login_id:
					server.login(login_id, password)
				server.sendmail(sender, recipients, message.as_string())
		elif security == "starttls":
			context = ssl.create_default_context()
			with smtplib.SMTP(host, port, timeout=30) as server:
				server.ehlo()
				server.starttls(context=context)
				server.ehlo()
				if enable_smtp_auth and login_id:
					server.login(login_id, password)
				server.sendmail(sender, recipients, message.as_string())
		elif security == "none":
			with smtplib.SMTP(host, port, timeout=30) as server:
				if enable_smtp_auth and login_id:
					server.login(login_id, password)
				server.sendmail(sender, recipients, message.as_string())
		else:
			logger.error("Unsupported SMTP security mode: %s", security)
			return False

		logger.info("Email sent to %s via SMTP", recipients)
		return True
	except Exception as e:
		logger.error("Failed to send email via SMTP: %s", e, exc_info=True)
		return False