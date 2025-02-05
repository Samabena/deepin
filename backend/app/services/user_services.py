from jinja2 import Template
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Depends, Request, status
from app.schemas.schemas import UserCreate
from sqlalchemy.orm import Session
from app.crud.crud import create_user ,authenticate_user, create_session, clear_session # get_user_by_id,
from app.models.models import User
from datetime import datetime
from app.db.database import get_db
import secrets


SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")  
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME") 


# Load the template file
def load_template(template_file_path: str):
    with open(template_file_path, 'r') as file:
        return Template(file.read())


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

        subject = "Bienvenue à Nos Formations - Confirmation d'inscription"

        # Try sending via SendGrid first
        sendgrid_success = await send_email_via_sendgrid(email, subject, rendered_template)

        # If SendGrid fails, fallback to SMTP
        if not sendgrid_success:
            await send_email_via_smtp(email, rendered_template)

    except Exception as e:
        print(f"❌ Erreur générale d'envoi d'email: {e}")




# EXTERNAL PROVIDER : Sendgrid
async def send_email_via_sendgrid(email: str, subject: str, html_content: str):

    """Send email using SendGrid"""
    try:
        message = Mail(
            from_email=(MAIL_FROM, MAIL_FROM_NAME),
            to_emails=email,
            subject=subject,  
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




# REGISTRATION AND EMAIL VERIFICATION USING TOKEN GENERATION

BASE_URL = os.getenv("BASE_URL")

async def register_user(db: Session, user: UserCreate):
    
    try:
        # Register user in the database
        new_user = create_user(db=db, user=user)

        # Generate verification link using user ID and token
        verification_link = f"{BASE_URL}/verify/{new_user.id}?token={new_user.verification_token}"
        
        # Load the email template
        email_template = load_template("app/templates/email_verification.html")

        # Render the template with values
        rendered_template = email_template.render(fullname=new_user.fullname, verification_link=verification_link)

        subject = "Bienvenue sur In Deep AI  - Verification d'Email"
        # Sending via Sendgrid
        sendgrid_success = await send_email_via_sendgrid(new_user.email, subject, rendered_template)
        
        # If SendGrid fails, fallback to SMTP
        if not sendgrid_success:
            await send_email_via_smtp(new_user.email, subject, rendered_template)

    except Exception as e:
        print(f"❌ Erreur générale d'envoi d'email: {e}")
    finally:
        db.close()



# User Verification Function
def verify_user_account(db: Session,user_id: int, token: str):
    user = db.query(User).filter(User.id == user_id, User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found or token invalid")
    
    user.is_verified = True
    user.verification_token = None  # Clear the token after verification
    db.commit()
    db.refresh(user)
    return {"message": "User verified successfully"}


# User Login Function
def login_user(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=400, detail="Identifiants invalides")
    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Email non vérifié")
    user = create_session(db, user.id)
    formatted_name = user.fullname.lower().replace(" ", "-")
    return user, f"/admin/{formatted_name}"

def logout_user(db: Session, user_id: int):
    clear_session(db, user_id)



#Verify if user is connected 

def get_current_user(request: Request, db: Session = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if not session_token:
        # You can either raise an exception or redirect to login
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    user = db.query(User).filter(
        User.session_token == session_token,
        User.session_expiry > datetime.now()
    ).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")
    
    return user


# Service to update password

async def forgot_password_service(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Email non trouvé")

    # Générer un token de réinitialisation
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    db.commit()

    # Créer un lien de réinitialisation à envoyer par email
    reset_link = f"{BASE_URL}/password-update/{user.id}?token={reset_token}"

    rendered_template = f"Bonjour {user.fullname}, veuillez réinitialiser votre mot de passe en cliquant sur le lien suivant : {reset_link}"

    subject = "Demande de réinitialisation de mot de passe"
    # Sending via Sendgrid
    sendgrid_success = await send_email_via_sendgrid(user.email, subject, rendered_template)

    return {"message": "Si votre email est enregistré, vous recevrez un lien de réinitialisation de mot de passe."}

