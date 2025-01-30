from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import engine, Base, get_db
from app.models.models import Registration
from app.schemas.schemas import RegistrationCreate
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi import BackgroundTasks
from app.services.user_services import send_registration_email
from app.services.user_services import send_email  






app = FastAPI()

# Allow CORS for all origins and methods (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],  # Adjust to allowed methods
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

# Create database tables
Base.metadata.create_all(bind=engine)


app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/nos-formations", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("formation.html", {"request": request})


@app.get("/contactez-nous", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})



# REGISTRATION ROUTE

@app.post("/register", status_code=status.HTTP_201_CREATED)
def create_registration(data: RegistrationCreate, db: Session = Depends(get_db), background_tasks: BackgroundTasks = BackgroundTasks()):
    # Check if the email is already registered for the same course
    existing_registration = db.query(Registration).filter(
        Registration.email == data.email,
        Registration.preferred_course == data.preferred_course
    ).first()
    
    if existing_registration:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vous êtes déjà inscrit à ce cours.")

    # Add registration to the database
    new_registration = Registration(
        full_name=data.full_name,
        whatsapp_number=data.whatsapp_number,
        email=data.email,
        gender=data.gender,
        preferred_course=data.preferred_course,
        agreement=data.agreement,
    )
    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)

    # Send email asynchronously
    background_tasks.add_task(send_registration_email, new_registration.full_name, new_registration.email, new_registration.preferred_course)
    
    return {"message": "Inscription réussie ! Veuillez consulter votre boîte e-mail.", "registration_id": new_registration.id}



@app.post("/send-message")
async def send_message(
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
):
    return send_email(name, email, subject, message)