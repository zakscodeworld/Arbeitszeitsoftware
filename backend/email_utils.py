import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import date, datetime, timedelta
import logging
from typing import Optional, Tuple

# Configure logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Email server configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.strato.de")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "webmaster@zaksprojects.de")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "Zaka123123!!")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "webmaster@zaksprojects.de")
SENDER_NAME = os.getenv("SENDER_NAME", "BBQ GmbH Zeiterfassung")

# Set default production URL if no environment variable is set
DEFAULT_APP_URL = "https://zaksprojects.de/zeiterfassung"
APP_URL = os.environ.get("APP_URL")
if not APP_URL or "localhost" in APP_URL:
    APP_URL = DEFAULT_APP_URL
    os.environ["APP_URL"] = APP_URL  # Force update the environment variable

EMAIL_ENABLED = os.getenv("DISABLE_EMAIL_SENDING", "False").lower() != "true"

# CSS styling for emails
EMAIL_STYLE = """
<style>
    body { font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
    h1 { color: #004a99; border-bottom: 2px solid #004a99; padding-bottom: 10px; }
    .highlight { background-color: #f0f7ff; padding: 15px; border-left: 4px solid #004a99; margin: 20px 0; }
    .footer { margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; font-size: 0.9em; color: #666; }
    .hours { font-size: 1.2em; font-weight: bold; color: #004a99; }
    .btn { display: inline-block; background-color: #004a99; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; margin-top: 15px; }
</style>
"""

def send_email(to_email: str, subject: str, message_html: str, message_text: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """Send an email with HTML and optional plain text content"""
    if not EMAIL_ENABLED:
        logger.info(f"Email sending is disabled. Would send to: {to_email}")
        return True, None

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg['To'] = to_email

        if not message_text:
            import re
            message_text = message_html.replace('<br>', '\n').replace('</p>', '\n').replace('<li>', '- ')
            message_text = re.sub(r'<[^>]*>', '', message_text)

        msg.attach(MIMEText(message_text, 'plain', 'utf-8'))
        msg.attach(MIMEText(message_html, 'html', 'utf-8'))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            logger.info(f"Email sent successfully to {to_email}")
            return True, None

    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to send email to {to_email}: {error_message}")
        return False, error_message

def send_work_hours_notification(user_email: str, user_name: str, date_str: str, hours: float, is_under: bool = True) -> bool:
    """Send notification about work hours being under or over the standard 8-hour workday"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        formatted_date = date_obj.strftime("%d.%m.%Y")
        weekday = date_obj.strftime("%A")
    except:
        formatted_date = date_str
        weekday = "Tag"

    arbeitszeiten_url = f"{APP_URL}/arbeitszeiten.html"
    diff_hours = abs(8 - hours)
    
    if is_under:
        subject = f"Arbeitszeit unterschritten am {weekday}, {formatted_date}"
        html_content = f"""
        <html>
        <head>{EMAIL_STYLE}</head>
        <body>
            <h1>Arbeitszeit-Benachrichtigung</h1>
            <p>Guten Tag {user_name},</p>
            
            <div class="highlight">
                <p>Ihre erfasste Arbeitszeit für {weekday}, den <strong>{formatted_date}</strong> 
                beträgt <span class="hours">{hours:.2f} Stunden</span>, was unter der Standardarbeitszeit von 8 Stunden liegt.</p>
                <p>Differenz: <span class="hours">-{diff_hours:.2f} Stunden</span></p>
            </div>
            
            <p>Bitte überprüfen Sie diesen Eintrag und ergänzen Sie ihn bei Bedarf. Mögliche Gründe:</p>
            <ul>
                <li>Unvollständige Zeiterfassung</li>
                <li>Teilzeittag</li>
                <li>Urlaub oder Krankheit (bitte dokumentieren)</li>
            </ul>
            
            <a href="{arbeitszeiten_url}" class="btn">Zeiterfassung öffnen</a>
            
            <div class="footer">
                <p>Mit freundlichen Grüßen,<br>Ihr BBQ GmbH Zeiterfassungssystem</p>
                <p>Diese E-Mail wurde automatisch generiert. Bitte antworten Sie nicht auf diese E-Mail.</p>
            </div>
        </body>
        </html>
        """
    else:
        subject = f"Arbeitszeit überschritten am {weekday}, {formatted_date}"
        html_content = f"""
        <html>
        <head>{EMAIL_STYLE}</head>
        <body>
            <h1>Arbeitszeit-Benachrichtigung</h1>
            <p>Guten Tag {user_name},</p>
            
            <div class="highlight">
                <p>Ihre erfasste Arbeitszeit für {weekday}, den <strong>{formatted_date}</strong> 
                beträgt <span class="hours">{hours:.2f} Stunden</span>, was über der Standardarbeitszeit von 8 Stunden liegt.</p>
                <p>Differenz: <span class="hours">+{diff_hours:.2f} Stunden</span></p>
            </div>
            
            <p>Bitte überprüfen Sie diesen Eintrag auf Richtigkeit:</p>
            <a href="{arbeitszeiten_url}" class="btn">Zeiterfassung öffnen</a>
            
            <div class="footer">
                <p>Mit freundlichen Grüßen,<br>Ihr BBQ GmbH Zeiterfassungssystem</p>
                <p>Diese E-Mail wurde automatisch generiert. Bitte antworten Sie nicht auf diese E-Mail.</p>
            </div>
        </body>
        </html>
        """

    success, error = send_email(user_email, subject, html_content)
    if not success:
        logger.error(f"Failed to send work hours notification: {error}")
    return success

def send_password_changed_notification(user_email: str, user_name: str, change_time: Optional[datetime] = None) -> bool:
    """Send notification that the user's password has been changed"""
    if change_time is None:
        change_time = datetime.now()
    
    formatted_time = change_time.strftime("%d.%m.%Y um %H:%M Uhr")
    login_url = f"{APP_URL}/login.html"
    subject = "Passwortänderung bestätigt"
    
    html_content = f"""
    <html>
    <head>{EMAIL_STYLE}</head>
    <body>
        <h1>Passwortänderung bestätigt</h1>
        <p>Guten Tag {user_name},</p>
        
        <div class="highlight">
            <p>Ihr Passwort wurde am <strong>{formatted_time}</strong> erfolgreich geändert.</p>
        </div>
        
        <p>Falls Sie diese Änderung nicht selbst vorgenommen haben, kontaktieren Sie bitte umgehend Ihren Administrator oder das IT-Support-Team.</p>
        
        <p>Sie können sich hier mit Ihrem neuen Passwort anmelden:</p>
        <a href="{login_url}" class="btn">Zum Login</a>
        
        <div class="footer">
            <p>Mit freundlichen Grüßen,<br>Ihr BBQ GmbH Zeiterfassungssystem</p>
            <p>Diese E-Mail wurde automatisch generiert. Bitte antworten Sie nicht auf diese E-Mail.</p>
        </div>
    </body>
    </html>
    """
    
    success, error = send_email(user_email, subject, html_content)
    if not success:
        logger.error(f"Failed to send password change notification: {error}")
    return success

def send_account_created_notification(user_email: str, user_name: str, username: str, temp_password: Optional[str] = None) -> bool:
    """Send notification that a new account has been created"""
    login_url = f"{APP_URL}/login.html"
    subject = "Willkommen bei BBQ GmbH Zeiterfassung"
    
    password_section = ""
    if temp_password:
        password_section = f"""
        <p><strong>Temporäres Passwort:</strong> {temp_password}</p>
        <p>Bitte ändern Sie dieses Passwort nach Ihrem ersten Login.</p>
        """
    
    html_content = f"""
    <html>
    <head>{EMAIL_STYLE}</head>
    <body>
        <h1>Willkommen bei BBQ GmbH Zeiterfassung</h1>
        <p>Guten Tag {user_name},</p>
        
        <div class="highlight">
            <p>Ihr Benutzerkonto wurde erfolgreich erstellt.</p>
            <p><strong>Benutzername:</strong> {username}</p>
            {password_section}
        </div>
        
        <p>Mit diesem Konto können Sie Ihre Arbeitszeiten erfassen, Urlaubsanträge stellen und vieles mehr.</p>
        
        <p>Sie können sich hier anmelden:</p>
        <a href="{login_url}" class="btn">Zum Login</a>
        
        <div class="footer">
            <p>Mit freundlichen Grüßen,<br>Ihr BBQ GmbH Zeiterfassungssystem</p>
            <p>Diese E-Mail wurde automatisch generiert. Bitte antworten Sie nicht auf diese E-Mail.</p>
        </div>
    </body>
    </html>
    """
    
    success, error = send_email(user_email, subject, html_content)
    if not success:
        logger.error(f"Failed to send account creation notification: {error}")
    return success
