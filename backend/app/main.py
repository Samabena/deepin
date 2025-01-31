from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import engine, Base, get_db
from app.models.models import Registration, BlogPost
from app.schemas.schemas import RegistrationCreate
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi import BackgroundTasks
from app.services.user_services import send_registration_email
from app.services.user_services import send_email  
from datetime import datetime
from sqlalchemy import extract





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


@app.get("/admin", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request, "show_navbar": False})



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





@app.post("/submit-blog")
async def submit_blog(
    header_image: str = Form(...),
    title: str = Form(...),
    author: str = Form(...),
    about_author: str = Form(...),
    publication_date: str = Form(...),
    reading_time: int = Form(...),
    introduction: str = Form(...),
    section_1_title: str = Form(...),
    section_1_content: str = Form(...),
    quote: str = Form(None),
    section_2_title: str = Form(...),
    section_2_content: str = Form(...),
    tools: str = Form(None),
    section_3_title: str = Form(...),
    section_3_content: str = Form(...),
    conclusion: str = Form(...),
    cta: str = Form(None),
    db: Session = Depends(get_db)
):
    # ✅ Validate & Parse `publication_date`
    try:
        pub_date = datetime.strptime(publication_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="📅 Date de publication invalide. Format attendu: YYYY-MM-DD")

    # ✅ Create new blog post
    new_post = BlogPost(
        header_image=header_image,
        title=title,
        author=author,
        about_author=about_author,
        publication_date=pub_date,
        reading_time=reading_time,
        introduction=introduction,
        section_1_title=section_1_title,
        section_1_content=section_1_content,
        quote=quote,
        section_2_title=section_2_title,
        section_2_content=section_2_content,
        tools=tools,
        section_3_title=section_3_title,
        section_3_content=section_3_content,
        conclusion=conclusion,
        cta=cta
    )

    

    db.add(new_post)
    db.commit()
    db.refresh(new_post)  

     # ✅ Redirect to the newly created blog post
    return RedirectResponse(url=f"/blog/{new_post.publication_date.year}/{new_post.publication_date.month}/{new_post.id}", status_code=303)




BASE_YEAR = 2025  

@app.get("/blog/{year}/{month}/{post_id}")
async def get_blog_post(year: int, month: int, post_id: int, request: Request, db: Session = Depends(get_db)):
    # ✅ Fetch the current post
    post = db.query(BlogPost).filter(
        BlogPost.id == post_id,
        extract("year", BlogPost.publication_date) == year,
        extract("month", BlogPost.publication_date) == month
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="🛑 Article non trouvé!")

    # ✅ Find the previous post (Going backward)
    prev_post = (
        db.query(BlogPost)
        .filter(
            (BlogPost.publication_date < post.publication_date) |
            ((BlogPost.publication_date == post.publication_date) & (BlogPost.id < post.id))
        )
        .order_by(BlogPost.publication_date.desc(), BlogPost.id.desc())
        .first()
    )

    # ✅ If no previous post in the current month, check the previous month
    if not prev_post and (year > BASE_YEAR or (year == BASE_YEAR and month > 1)):
        prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
        prev_post = (
            db.query(BlogPost)
            .filter(
                extract("year", BlogPost.publication_date) == prev_year,
                extract("month", BlogPost.publication_date) == prev_month
            )
            .order_by(BlogPost.publication_date.desc(), BlogPost.id.desc())
            .first()
        )

    # ✅ Find the next post (Going forward)
    next_post = (
        db.query(BlogPost)
        .filter(
            (BlogPost.publication_date > post.publication_date) |
            ((BlogPost.publication_date == post.publication_date) & (BlogPost.id > post.id))
        )
        .order_by(BlogPost.publication_date.asc(), BlogPost.id.asc())
        .first()
    )

    # ✅ If no next post in the current month, check the next month
    if not next_post:
        next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
        next_post = (
            db.query(BlogPost)
            .filter(
                extract("year", BlogPost.publication_date) == next_year,
                extract("month", BlogPost.publication_date) == next_month
            )
            .order_by(BlogPost.publication_date.asc(), BlogPost.id.asc())
            .first()
        )

    return templates.TemplateResponse("single_post.html", {
        "request": request,
        "post": post,
        "prev_post": prev_post,
        "next_post": next_post
    })




@app.get("/blog", response_class=HTMLResponse)
async def get_blogs(request: Request, db: Session = Depends(get_db), page: int = Query(1, alias="page")):
    POSTS_PER_PAGE = 6

    # Count total posts
    total_posts = db.query(BlogPost).count()

    # Fetch posts with limit & offset for pagination
    posts = (
        db.query(BlogPost)
        .order_by(BlogPost.publication_date.desc())  # Newest first
        .offset((page - 1) * POSTS_PER_PAGE)
        .limit(POSTS_PER_PAGE)
        .all()
    )

    # Determine if there are more pages
    total_pages = (total_posts + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE
    has_next = page < total_pages
    has_prev = page > 1

    return templates.TemplateResponse("blog.html", {
        "request": request,
        "posts": posts,
        "page": page,
        "has_next": has_next,
        "has_prev": has_prev
    })
