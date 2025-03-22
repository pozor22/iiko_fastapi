import base64
import aiosmtplib
from email.message import EmailMessage
from jinja2 import Template

from settings.config import EMAIL_USER, EMAIL_PASSWORD, EM_PORT, EM_HOST


async def send_email_active_account(user_id: int, email: str, username: str):
    uid = base64.urlsafe_b64encode(str(user_id).encode()).decode()
    token = "some_generated_token"

    template_str = """
    <html>
    <body>
        <p>Привет, {{ username }}!</p>
        <p>Пожалуйста, подтвердите ваш аккаунт, перейдя по ссылке:</p>
        <a href="http://localhost:8000/core/{{ uid }}/{{ token }}">Подтвердить аккаунт</a>
    </body>
    </html>
    """
    template = Template(template_str)
    message_body = template.render(username=username, uid=uid, token=token)

    # Формирование email-сообщения
    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = email
    msg["Subject"] = "Подтверждение аккаунта"
    msg.set_content(message_body, subtype="html")

    await aiosmtplib.send(
        msg,
        hostname=EM_HOST,
        port=EM_PORT,
        start_tls=True,
        username=EMAIL_USER,
        password=EMAIL_PASSWORD
    )

    return f"Email отправлен пользователю {username}"


async def send_email_change_password(code: int, email: str, username: str):
    template_str = """
    <html>
    <body>
        <p>Привет, {{ username }}!</p>
        <p>Пожалуйста, подтвердите смену пароля с помощью данного кода</p>
        <h3>Ваш код: {{ code }}</h3>
    </body>
    </html>
    """
    template = Template(template_str)
    message_body = template.render(username=username, code=code)

    # Формирование email-сообщения
    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = email
    msg["Subject"] = "Подтверждение аккаунта"
    msg.set_content(message_body, subtype="html")

    await aiosmtplib.send(
        msg,
        hostname=EM_HOST,
        port=EM_PORT,
        start_tls=True,
        username=EMAIL_USER,
        password=EMAIL_PASSWORD
    )

    return f"Email отправлен пользователю {username}"
