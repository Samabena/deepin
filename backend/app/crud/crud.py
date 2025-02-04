import secrets
from sqlalchemy.orm import Session
from app.models.models import User
from app.schemas.schemas import UserCreate
from passlib.context import CryptContext
from datetime import datetime
from fastapi import HTTPException
from datetime import datetime, timedelta



pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):


    # Check if the username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail={"error": "username_exists", "suggestion": generate_suggestions(user.username, user.fullname)}
        )
    
     # Check if the email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail={"error": "email_exists"})

    password = user.password
    hashed_password = pwd_context.hash(password)
    
    verification_token = secrets.token_urlsafe(32)
    
      # Generate a secure token for email verification
    
    db_user = User(
        username=user.username,
        fullname=user.fullname,
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False,
        verification_token=verification_token,
        session_token=None,  
        session_expiry=None ,
        reset_token = None
    )
    

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    
    return db_user


def verify_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_verified = True
        db.commit()
        db.refresh(user)
    return user

# for login 

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

def create_session(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        session_token = secrets.token_hex(16)
        session_expiry = datetime.now() + timedelta(hours=2)  # Set session expiry time
        user.session_token = session_token
        user.session_expiry = session_expiry
        db.commit()
        db.refresh(user)
    return user

def clear_session(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.session_token = None
        user.session_expiry = None
        db.commit()
        db.refresh(user)

# Add a function to get user by session token
def get_user_by_session_token(db: Session, session_token: str):
    return db.query(User).filter(User.session_token == session_token, User.session_expiry > datetime.now()).first()


def generate_suggestions(username, fullname):
    # Generate a list of suggested usernames by combining fullname and some random numbers
    suggestions = []
    for i in range(1, 4):
        suggestions.append(f"{fullname}{i}")
    return suggestions

def update_user_password(
    db: Session, user_id: int, token: str, new_password: str, confirm_password: str
):
    # Query the user and validate the reset token
    user = db.query(User).filter(User.id == user_id, User.reset_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Validate passwords match
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Hash the new password and update user information
    hashed_password = pwd_context.hash(new_password)
    user.hashed_password = hashed_password
    user.reset_token = None  # Invalidate the reset token
    db.commit()

    return {"message": f"{user.fullname}, you have successfully changed your password. Please go back to the login page."}


def get_profile_picture(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.profile_picture


# for login 

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

def create_session(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        session_token = secrets.token_hex(16)
        session_expiry = datetime.now() + timedelta(hours=2)  # Set session expiry time
        user.session_token = session_token
        user.session_expiry = session_expiry
        db.commit()
        db.refresh(user)
    return user

def clear_session(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.session_token = None
        user.session_expiry = None
        db.commit()
        db.refresh(user)


def update_user_password(
    db: Session, user_id: int, token: str, new_password: str, confirm_password: str
):
    # Rechercher l'utilisateur et valider le token de réinitialisation
    user = db.query(User).filter(User.id == user_id, User.reset_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
    
    # Vérifier que les mots de passe correspondent
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Les mots de passe ne correspondent pas")

    # Hasher le nouveau mot de passe et mettre à jour les informations de l'utilisateur
    hashed_password = pwd_context.hash(new_password)
    user.hashed_password = hashed_password
    user.reset_token = None  # Invalider le token de réinitialisation
    db.commit()

    return {"message": f"{user.fullname}, vous avez modifié votre mot de passe avec succès. Veuillez retourner sur la page de connexion."}
