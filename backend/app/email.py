"""
Módulo de envío de correos electrónicos — Resend
"""
import logging
import resend

from app.config import settings

logger = logging.getLogger(__name__)


def _init():
    resend.api_key = settings.RESEND_API_KEY


def _base_html(title: str, body_content: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/></head>
<body style="margin:0;padding:0;background:#f0f8ff;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f8ff;padding:40px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,106,180,.10);">
        <tr>
          <td style="background:#006ab4;padding:32px 40px;text-align:center;">
            <p style="margin:0;font-size:22px;font-weight:700;color:#fff;letter-spacing:.02em;">✦ Funerarias Rancier</p>
          </td>
        </tr>
        <tr>
          <td style="padding:40px 40px 32px;">
            {body_content}
          </td>
        </tr>
        <tr>
          <td style="background:#f8f8f8;padding:20px 40px;text-align:center;border-top:1px solid #eee;">
            <p style="margin:0;font-size:11px;color:#aaa;">© 2025 Funerarias Rancier · República Dominicana</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _send(to: str, subject: str, html: str) -> bool:
    if not settings.RESEND_API_KEY:
        logger.warning("RESEND_API_KEY no configurada — email no enviado a %s", to)
        return False
    _init()
    try:
        resend.Emails.send({"from": settings.EMAIL_FROM, "to": [to], "subject": subject, "html": html})
        logger.info("Email enviado a %s | %s", to, subject)
        return True
    except Exception as exc:
        logger.error("Error enviando email a %s: %s", to, exc)
        return False


def send_verification_email(to_email: str, nombre: str, token: str) -> bool:
    url = f"{settings.BACKEND_URL}/verify-email/{token}"
    body = f"""
      <h1 style="margin:0 0 12px;font-size:22px;font-weight:700;color:#006ab4;">Verifica tu correo electrónico</h1>
      <p style="margin:0 0 8px;font-size:15px;color:#444;line-height:1.6;">Hola <strong>{nombre}</strong>,</p>
      <p style="margin:0 0 28px;font-size:15px;color:#444;line-height:1.6;">
        Gracias por registrarte. Para activar tu cuenta haz clic en el botón:
      </p>
      <table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
        <a href="{url}" style="display:inline-block;background:#00a9e1;color:#fff;font-size:13px;font-weight:700;
           letter-spacing:.1em;text-transform:uppercase;text-decoration:none;padding:14px 36px;border-radius:6px;">
          Verificar mi cuenta
        </a>
      </td></tr></table>
      <p style="margin:28px 0 0;font-size:12px;color:#999;line-height:1.6;">
        O copia este enlace:<br/>
        <a href="{url}" style="color:#00a9e1;word-break:break-all;">{url}</a>
      </p>
      <p style="margin:20px 0 0;font-size:12px;color:#bbb;">Si no creaste esta cuenta, ignora este correo.</p>
    """
    return _send(to_email, "Verifica tu correo — Funerarias Rancier", _base_html("Verificación", body))


def send_contact_notification(nombre: str, email: str, telefono: str, asunto: str, mensaje: str, archivo_url: str = None) -> bool:
    """Notifica al admin cuando llega un mensaje del formulario de contacto."""
    archivo_html = ""
    if archivo_url:
        full_url = f"{settings.BACKEND_URL}{archivo_url}"
        archivo_html = f'<p style="margin:12px 0 0;font-size:13px;color:#444;"><strong>📎 Archivo adjunto:</strong> <a href="{full_url}" style="color:#00a9e1;">{full_url}</a></p>'

    body = f"""
      <h1 style="margin:0 0 16px;font-size:20px;font-weight:700;color:#006ab4;">📬 Nuevo mensaje de contacto</h1>
      <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
        <tr><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#666;width:120px;">Nombre</td><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#333;font-weight:600;">{nombre}</td></tr>
        <tr><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#666;">Correo</td><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#333;"><a href="mailto:{email}" style="color:#00a9e1;">{email}</a></td></tr>
        <tr><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#666;">Teléfono</td><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#333;">{telefono or "No indicado"}</td></tr>
        <tr><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#666;">Asunto</td><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#333;">{asunto or "Sin asunto"}</td></tr>
      </table>
      <div style="margin:20px 0 0;padding:16px;background:#f0f8ff;border-radius:8px;border-left:4px solid #00a9e1;">
        <p style="margin:0;font-size:13px;color:#444;line-height:1.7;white-space:pre-wrap;">{mensaje}</p>
      </div>
      {archivo_html}
      <p style="margin:20px 0 0;font-size:12px;color:#999;">Responder directamente a: <a href="mailto:{email}" style="color:#00a9e1;">{email}</a> | Tel: {telefono or "N/A"}</p>
    """
    return _send(settings.ADMIN_EMAIL, f"📬 Contacto: {asunto or nombre} — Funerarias Rancier", _base_html("Contacto", body))


def send_plan_notification(nombre: str, email: str, telefono: str, plan_nombre: str, cedula: str, documento_url: str = None) -> bool:
    """Notifica al admin cuando un cliente solicita contratar un plan."""
    doc_html = ""
    if documento_url:
        full_url = f"{settings.BACKEND_URL}{documento_url}"
        doc_html = f'<tr><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#666;">Documento</td><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;"><a href="{full_url}" style="color:#00a9e1;">Ver PDF adjunto</a></td></tr>'

    body = f"""
      <h1 style="margin:0 0 16px;font-size:20px;font-weight:700;color:#006ab4;">🎯 Nueva solicitud de plan</h1>
      <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
        <tr><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#666;width:120px;">Cliente</td><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#333;font-weight:600;">{nombre}</td></tr>
        <tr><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#666;">Correo</td><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#333;"><a href="mailto:{email}" style="color:#00a9e1;">{email}</a></td></tr>
        <tr><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#666;">Teléfono</td><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#333;">{telefono or "No indicado"}</td></tr>
        <tr><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#666;">Plan</td><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#333;font-weight:700;color:#006ab4;">{plan_nombre}</td></tr>
        <tr><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#666;">Cédula</td><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;color:#333;font-weight:600;">{cedula}</td></tr>
        {doc_html}
      </table>
      <p style="margin:20px 0 0;font-size:12px;color:#999;">Contactar al cliente: <a href="mailto:{email}" style="color:#00a9e1;">{email}</a> | Tel: {telefono or "N/A"}</p>
    """
    return _send(settings.ADMIN_EMAIL, f"🎯 Nuevo plan contratado: {plan_nombre} — {nombre}", _base_html("Plan", body))


def send_password_reset_email(to_email: str, nombre: str, token: str) -> bool:
    url = f"{settings.FRONTEND_URL}/login.html?reset_token={token}"
    body = f"""
      <h1 style="margin:0 0 12px;font-size:22px;font-weight:700;color:#006ab4;">Cambio de contraseña</h1>
      <p style="margin:0 0 8px;font-size:15px;color:#444;line-height:1.6;">Hola <strong>{nombre}</strong>,</p>
      <p style="margin:0 0 28px;font-size:15px;color:#444;line-height:1.6;">
        Recibimos una solicitud para cambiar la contraseña de tu cuenta. Haz clic en el botón para continuar.
        Este enlace expira en <strong>30 minutos</strong>.
      </p>
      <table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
        <a href="{url}" style="display:inline-block;background:#006ab4;color:#fff;font-size:13px;font-weight:700;
           letter-spacing:.1em;text-transform:uppercase;text-decoration:none;padding:14px 36px;border-radius:6px;">
          Cambiar contraseña
        </a>
      </td></tr></table>
      <p style="margin:28px 0 0;font-size:12px;color:#999;line-height:1.6;">
        O copia este enlace:<br/>
        <a href="{url}" style="color:#00a9e1;word-break:break-all;">{url}</a>
      </p>
      <p style="margin:20px 0 0;font-size:12px;color:#bbb;">
        Si no solicitaste este cambio, ignora este correo. Tu contraseña no será modificada.
      </p>
    """
    return _send(to_email, "Cambio de contraseña — Funerarias Rancier", _base_html("Reset", body))
