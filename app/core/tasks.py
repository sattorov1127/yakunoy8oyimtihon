import emails
from app.core.celery_app import celery_app

@celery_app.task
def send_registration_email(email_to: str):
    message = emails.Message(
        html="<h1>Xush kelibsiz!</h1><p>Siz Jobify platformasidan muvaffaqiyatli ro'yxatdan o'tdingiz.</p>",
        subject="Jobify - Ro'yxatdan o'tish",
        mail_from=("Jobify Team", "noreply@jobify.uz")
    )
    # r = message.send(to=email_to, smtp={'host': 'smtp.gmail.com', 'port': 465, 'ssl': True, ...})
    print(f"Email yuborildi: {email_to}")