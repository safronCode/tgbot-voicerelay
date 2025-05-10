import os, smtplib

from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
from storage.config import EMAIL_SENDER, EMAIL_PASSWORD



def email_sender(data: dict, EMAIL_ADDRESS: str):
    # Загружаем шаблон Jinja2
    template = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates'))).get_template("structure.html")
    html_content = template.render(data)

    # Настраиваем сообщение
    msg = EmailMessage()
    msg['Subject'] = 'SayAndDo | ' + data.get('subject', 'No subject')
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_ADDRESS
    msg.set_content("Ваш email-клиент не поддерживает HTML.")
    msg.add_alternative(html_content, subtype='html')

    # Отправляем письмо
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)


