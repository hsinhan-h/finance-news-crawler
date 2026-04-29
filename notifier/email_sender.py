"""
Email sender dispatcher.
Supports Gmail OAuth and generic SMTP backends.
"""
import logging

logger = logging.getLogger(__name__)

from notifier.gmail_sender import send_via_gmail_oauth
from notifier.smtp_sender import send_via_smtp


def send_report(config: dict, report_path: str, report_date: str) -> bool:
    """
    Send the report via the configured email backend.
    Returns True on success, False on failure.
    config is the email sub-dict from config.yaml.
    """
    method = str(config.get("method", "gmail_oauth")).lower()

    if method == "gmail_oauth":
        return send_via_gmail_oauth(config, report_path, report_date)
    if method == "smtp":
        return send_via_smtp(config, report_path, report_date)

    logger.error("Unsupported email method: %s", method)
    return False
