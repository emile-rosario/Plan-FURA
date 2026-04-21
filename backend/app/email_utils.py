import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    reset_url = f"{settings.FRONTEND_URL}/reset-password.html?token={reset_token}"

    subject = "Restablecer contraseña — Funerarias Rancier"
    body_html = f"""
    <html>
    <body style="font-family:'DM Sans',Arial,sans-serif;background:#f8fbff;padding:40px 20px">
      <div style="max-width:500px;margin:0 auto;background:white;border:1px solid #e0f0f8;border-radius:12px;padding:40px">
        <h2 style="color:#006ab4;font-family:Georgia,serif;margin-top:0">Funerarias Rancier</h2>
        <p style="color:#555;font-size:14px">Recibimos una solicitud para restablecer la contraseña de tu cuenta.</p>
        <p style="color:#555;font-size:14px">Haz clic en el botón a continuación. Este enlace expira en <strong>1 hora</strong>.</p>
        <div style="text-align:center;margin:30px 0">
          <a href="{reset_url}"
             style="background:#00a9e1;color:#fff;text-decoration:none;padding:14px 32px;border-radius:6px;font-weight:600;font-size:13px;letter-spacing:.08em;text-transform:uppercase">
            Restablecer Contraseña
          </a>
        </div>
        <p style="color:#999;font-size:12px">Si no solicitaste este cambio, ignora este correo. Tu contraseña permanece igual.</p>
        <p style="color:#ccc;font-size:11px;border-top:1px solid #f0f0f0;margin-top:24px;padding-top:16px">
          Funerarias Rancier · Santo Domingo, Rep. Dominicana
        </p>
      </div>
    </body>
    </html>
    """

    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(
            "SMTP no configurado. Enlace de restablecimiento para %s: %s",
            to_email, reset_url,
        )
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())

        logger.info("Email de reset enviado a: %s", to_email)
        return True
    except Exception as exc:
        logger.error("Error enviando email a %s: %s", to_email, exc)
        return False
