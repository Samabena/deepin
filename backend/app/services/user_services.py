from jinja2 import Template
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi.responses import JSONResponse


SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")  
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME") 


# SMTP Configuration (Fallback)
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=MAIL_FROM,
    MAIL_FROM_NAME = MAIL_FROM_NAME,
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=False,  
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False
)

fm = FastMail(conf)



# General Function to send email using internal and external provider
async def send_registration_email(full_name: str, email: str, preferred_course: str):
    try:
        # Load email template
        with open("app/templates/email_template.html", "r") as file:
            email_template = Template(file.read())

        # Render template
        rendered_template = email_template.render(
            fullname=full_name,
            email=email,
            preferred_course=preferred_course
        )

        # Try sending via SendGrid first
        sendgrid_success = await send_email_via_sendgrid(email, rendered_template)

        # If SendGrid fails, fallback to SMTP
        if not sendgrid_success:
            await send_email_via_smtp(email, rendered_template)

    except Exception as e:
        print(f"❌ Erreur générale d'envoi d'email: {e}")




# EXTERNAL PROVIDER : Sendgrid
async def send_email_via_sendgrid(email: str, html_content: str):
    """Send email using SendGrid"""
    try:
        message = Mail(
            from_email=(MAIL_FROM, MAIL_FROM_NAME),
            to_emails=email,
            subject="Bienvenue à Nos Formations - Confirmation d'inscription",
            html_content=html_content
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        if response.status_code == 202:
            print(f"✅ Email envoyé avec succès via SendGrid à {email}")
            return True
        else:
            print(f"⚠️ SendGrid a échoué: {response.status_code}, {response.body}")
            return False

    except Exception as e:
        print(f"❌ SendGrid Error: {e}")
        return False



# INTERNAL PROVIDER : FastMail : SMTP
async def send_email_via_smtp(email: str, html_content: str):
    """Send email using SMTP (fallback)"""
    try:
        message = MessageSchema(
            subject="Bienvenue à Nos Formations - Confirmation d'inscription",
            recipients=[email],
            body=html_content,
            subtype="html"
        )

        await fm.send_message(message)
        print(f"✅ Email envoyé avec succès via SMTP à {email}")

    except Exception as e:
        print(f"❌ SMTP Error: {e}")



# SENDING EMAIL TO SAME SERVER EMAIL FOR CONTACT US SESSION 

SENDER_EMAIL = "info@in-deep-ai.com"  
RECEIVER_EMAIL = "info@in-deep-ai.com"  

def send_email(name: str, email: str, subject: str, message: str):
    """
    Sends an email using SendGrid.
    """
    try:
        email_content = f"""
        <h3>New Contact Form Message</h3>
        <p><strong>Nom:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Sujet:</strong> {subject}</p>
        <p><strong>Message:</strong><br>{message}</p>
        """

        mail = Mail(
            from_email=Email(SENDER_EMAIL, "In Deep AI Team"),
            to_emails=RECEIVER_EMAIL,
            subject=f"New Message from {name} - {subject}",
            html_content=email_content
        )

        
        mail.reply_to = Email(email)

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(mail)

        if response.status_code == 202:
            return JSONResponse(content={"message": "Message envoyé avec succès !"}, status_code=200)
        else:
            return JSONResponse(content={"error": "Erreur lors de l'envoi du message."}, status_code=500)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
