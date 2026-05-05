from fastapi import APIRouter, HTTPException, status
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr

from app.core.config import settings

router = APIRouter(prefix="/contact", tags=["contact"])


class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str


def get_mail_config() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=settings.mail_password,
        MAIL_FROM=settings.mail_from,
        MAIL_PORT=settings.mail_port,
        MAIL_SERVER=settings.mail_server,
        MAIL_STARTTLS=settings.mail_starttls,
        MAIL_SSL_TLS=settings.mail_ssl_tls,
        USE_CREDENTIALS=True,
    )


@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def send_contact(data: ContactRequest) -> None:
    if not settings.mail_username or not settings.mail_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service mail non configuré",
        )

    body = f"""Nouveau message depuis devzair.fr

Nom : {data.name}
Email : {data.email}

Message :
{data.message}
"""

    message = MessageSchema(
        subject=f"[devZair] Message de {data.name}",
        recipients=[settings.mail_from],
        body=body,
        subtype=MessageType.plain,
        reply_to=[data.email],
    )

    try:
        fm = FastMail(get_mail_config())
        await fm.send_message(message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erreur lors de l'envoi : {e}",
        ) from e
