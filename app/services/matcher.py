from imap_tools import MailMessage

from app.models import Template


def find_matching_link(messages: list[MailMessage], template: Template) -> str | None:
   raise NotImplementedError("Логика сопоставления шаблона WP")
