from email.message import EmailMessage
import aiosmtplib

# Dati di configurazione
SMTP_HOST = "smtp-mail.outlook.com"
SMTP_PORT = 587
SMTP_USER = "noreply@ststrailerservice.se"  # La tua email aziendale Outlook
SMTP_PASSWORD = "la_tua_password_per_app"  # Password per app se usi 2FA

async def send_reset_email(to_email: str, link: str):
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = "Återställ lösenord – Verkstad"
    msg.set_content(f"Klicka på länken för att återställa ditt lösenord:\n{link}\n\nLänken är giltig i 1 timme.")

    # Invia l'email utilizzando Outlook SMTP server
    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        start_tls=True,  # Usa STARTTLS per la crittografia
        username=SMTP_USER,
        password=SMTP_PASSWORD,
    )
 