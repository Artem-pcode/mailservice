import re
from datetime import datetime, timezone
from imap_tools import MailMessage


def _get_message_type(msg: MailMessage) -> str:
    return msg.headers.get("x-steam-message-type", ("",))[0]


def find_recovery_code(messages: list[MailMessage]) -> dict | None:
    for msg in messages:
        if "steampowered.com" not in msg.from_:
            continue
            
        if _get_message_type(msg) != "CAccountRecoveryCodeEmail":
            continue
            
        text = msg.text or msg.html or ""
        
        match = re.search(r'([A-Z0-9]{5})', text, re.MULTILINE)
        if match:
            code = match.group(1)
            if not re.search(r'https?://[^\s]*' + re.escape(code), text):
                return {
                    'code': code,
                    'date': msg.date,
                    'timestamp_ago': _get_time_ago(msg.date)
                }
    
    return None


def find_login_code(messages: list[MailMessage]) -> dict | None:
    for msg in messages:
        if "steampowered.com" not in msg.from_:
            continue
            
        if _get_message_type(msg) != "CEmailSteamGuard_Web":
            continue
            
        text = msg.text or msg.html or ""
        
        match = re.search(r'([A-Z0-9]{5})', text, re.MULTILINE)
        if match:
            code = match.group(1)
            if not re.search(r'https?://[^\s]*' + re.escape(code), text):
                return {
                    'code': code,
                    'date': msg.date,
                    'timestamp_ago': _get_time_ago(msg.date)
                }
    
    return None


def find_removal_link(messages: list[MailMessage]) -> dict | None:
    for msg in messages:
        if "steampowered.com" not in msg.from_:
            continue
            
        if _get_message_type(msg) != "CSteamGuardRemovalConfirmation":
            continue
            
        text = msg.text or msg.html or ""
        
        # Ищем полную ссылку
        match = re.search(r'(https://store\.steampowered\.com/account/steamguarddisableverification\?[^\s\n]+)', text)
        if match:
            return {
                'link': match.group(1),
                'date': msg.date,
                'timestamp_ago': _get_time_ago(msg.date)
            }
    
    return None


def find_verification_link(messages: list[MailMessage]) -> dict | None:
    for msg in messages:
        if "steampowered.com" not in msg.from_:
            continue
            
        if _get_message_type(msg) != "CAccountCreationEmailVerification":
            continue
            
        text = msg.text or msg.html or ""
        
        match = re.search(r'(https://store\.steampowered\.com/account/newaccountverification\?[^\s\n]+)', text)
        if match:
            return {
                'link': match.group(1),
                'date': msg.date,
                'timestamp_ago': _get_time_ago(msg.date)
            }
    
    return None


def find_all_recovery_codes(messages: list[MailMessage]) -> list[dict]:
    results = []
    for msg in messages:
        if "steampowered.com" not in msg.from_:
            continue

        if "CAccountRecoveryCodeEmail" not in str(msg.headers):
            continue

        text = msg.text or msg.html or ""

        match = re.search(r'([A-Z0-9]{5})', text, re.MULTILINE)
        if match:
            code = match.group(1)
            if not re.search(r'https?://[^\s]*' + re.escape(code), text):
                results.append({
                    'code': code,
                    'date': msg.date,
                })

    results.sort(key=lambda x: x['date'], reverse=True)
    return results


def _get_time_ago(dt: datetime) -> str:
    if dt is None:
        return "неизвестно"

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    diff = now - dt
    
    seconds = int(diff.total_seconds())
    
    if seconds < 60:
        return f"{seconds} секунд назад"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} минут назад"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} часов назад"
    else:
        days = seconds // 86400
        return f"{days} дней назад"