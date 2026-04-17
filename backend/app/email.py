"""
Módulo de envío de correos electrónicos — Resend
"""
import logging
import resend

from app.config import settings

logger = logging.getLogger(__name__)


def _get_client() -> None:
    """Configura la API key de Resend."""
    resend.api_key = settings.RESEND_API_KEY


def send_verification_email(to_email: str, nombre: str, token: str) -> bool:
    """
    Envía el correo de verificación de email al nuevo usuario.
    Retorna True si se envió correctamente, False si hubo error.
    """
    if not settings.RESEND_API_KEY:
        logger.warning(
            "RESEND_API_KEY no configurada — email de verificación no enviado a %s",
            to_email,
        )
        return False

    _get_client()

    verification_url = f"{settings.BACKEND_URL}/verify-email/{token}"

    html_body = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>
<body style="margin:0;padding:0;background:#f0f8ff;font-family:'DM Sans',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f8ff;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,106,180,.10);">
          <!-- Header -->
          <tr>
            <td style="background:#006ab4;padding:32px 40px;text-align:center;">
              <p style="margin:0;font-size:22px;font-weight:700;color:#ffffff;letter-spacing:.02em;">
                ✦ Funerarias Rancier
              </p>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:40px 40px 32px;">
              <h1 style="margin:0 0 12px;font-size:22px;font-weight:700;color:#006ab4;">
                Verifica tu correo electrónico
              </h1>
              <p style="margin:0 0 8px;font-size:15px;color:#444;line-height:1.6;">
                Hola <strong>{nombre}</strong>,
              </p>
              <p style="margin:0 0 28px;font-size:15px;color:#444;line-height:1.6;">
                Gracias por registrarte. Para activar tu cuenta y poder acceder al portal de clientes,
                haz clic en el botón a continuación:
              </p>
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center">
                    <a href="{verification_url}"
                       style="display:inline-block;background:#00a9e1;color:#ffffff;font-size:13px;font-weight:700;
                              letter-spacing:.1em;text-transform:uppercase;text-decoration:none;
                              padding:14px 36px;border-radius:6px;">
                      Verificar mi cuenta
                    </a>
                  </td>
                </tr>
              </table>
              <p style="margin:28px 0 0;font-size:12px;color:#999;line-height:1.6;">
                Si no puedes hacer clic en el botón, copia y pega este enlace en tu navegador:<br/>
                <a href="{verification_url}" style="color:#00a9e1;word-break:break-all;">{verification_url}</a>
              </p>
              <p style="margin:20px 0 0;font-size:12px;color:#bbb;">
                Si no creaste esta cuenta, puedes ignorar este correo.
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background:#f8f8f8;padding:20px 40px;text-align:center;border-top:1px solid #eee;">
              <p style="margin:0;font-size:11px;color:#aaa;">
                © 2025 Funerarias Rancier · República Dominicana
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    try:
        resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [to_email],
            "subject": "Verifica tu correo — Funerarias Rancier",
            "html": html_body,
        })
        logger.info("Email de verificación enviado a %s", to_email)
        return True
    except Exception as exc:
        logger.error("Error enviando email de verificación a %s: %s", to_email, exc)
        return False
