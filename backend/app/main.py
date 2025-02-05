from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import engine, Base, get_db
from app.models.models import Registration, BlogPost, User
from app.schemas.schemas import RegistrationCreate, UserCreate
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi import BackgroundTasks
from app.services.user_services import send_registration_email, verify_user_account, login_user, logout_user, send_email , register_user, get_current_user, forgot_password_service
from datetime import datetime, timedelta
from sqlalchemy import extract
from typing import Optional
from dotenv import load_dotenv
from jose import jwt 
import os
from app.crud.crud import update_user_password

app = FastAPI()


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

def secure_url_for(request, name, **path_params):
    url = request.url_for(name, **path_params)
    secure_url = url.replace(scheme="https")
    return secure_url



templates.env.globals["secure_url_for"] = secure_url_for


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/nos-formations", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("formation.html", {"request": request})


@app.get("/contactez-nous", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/admin-login", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request, "show_navbar": False})


@app.get("/admin-registration", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("admin_register.html", {"request": request, "show_navbar": False})

@app.get("/forgot-password", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("forgot.html", {"request": request, "show_navbar": False})

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
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
        cta=cta,
        user_id=current_user.id 
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



# User Registration Endpoint
@app.post("/registration/")

async def register_user_endpoint(
    username: str = Form(...),
    fullname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    This endpoint handles user registration.
    It takes user data and calls the register_user service.
    """
    try:

        # Convert form fields to UserCreate schema
        user = UserCreate(
            username=username,
            fullname=fullname,
            email=email,
            password=password
        )
        
        response = await register_user(db=db, user=user)
        
        print("User registered successfully, response:", response)
        return JSONResponse(content=response)
    
    except HTTPException as e:
        print("HTTP Exception:", str(e))
        raise e



# Verification endpoint (GET)

@app.get("/verify/{user_id}")
def verify_user_endpoint(user_id: int, request: Request, token: str = Query(None), db: Session = Depends(get_db)):
    """
    This endpoint verifies a user's email.
    It takes user ID and a token to verify the user.
    """
    try:
        if not token:
            # If the token is missing, render verification failed page with a generic message
            return templates.TemplateResponse("verification_failed.html", {"request": request, "message": "Unauthorized access", "no_navbar": True})
        
        # Attempt to verify the user with the provided token
        is_verified = verify_user_account(db=db, user_id=user_id, token=token)
        
        if is_verified:
            # Render verification success page
            return templates.TemplateResponse("verification_success.html", {"request": request, "no_navbar": True})
        else:
            # Render verification failed page with generic message
            return templates.TemplateResponse("verification_failed.html", {"request": request, "message": "Verification failed. Please try again.", "show_navbar": False})
    
    except HTTPException as e:
        # Log detailed error and render verification failed page for HTTP exceptions
        print("HTTP Exception:", str(e))
        return templates.TemplateResponse("verification_failed.html", {"request": request, "message": "Unauthorized access", "show_navbar": False})
    
    except Exception as e:
        # Log unexpected errors and render verification failed page
        print("Unexpected Error:", str(e))
        return templates.TemplateResponse("verification_failed.html", {"request": request, "message": "Internal server error. Please try again later.", "show_navbar": False})
    


# SECURE LOGIN 

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(hours=1)  # Token expiration
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/login/")
def login(
    response: Response,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
    redirect: Optional[str] = None
):
    try:
        user, redirect_url = login_user(db, email, password)

        # Create JWT token
        access_token = create_access_token(data={"sub": str(user.id)})

        # Set the token in cookies (optional)
        response.set_cookie(key="session_token", value=user.session_token, httponly=True)
        response.set_cookie(key="access_token", value=access_token, httponly=True)

        if redirect:
            redirect_url = redirect

        return {"message": "Login successful", "redirect_url": redirect_url, "access_token": access_token}
    except HTTPException as e:
        raise e
    


@app.get("/admin/{fullname}")
def home(request: Request, fullname: str, db: Session = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if not session_token:
        # Redirect to login with a custom message
        return RedirectResponse(url=f"/login?message=not_logged_in")

    user = db.query(User).filter(User.session_token == session_token, User.session_expiry > datetime.now()).first()
    if not user:
        # Redirect to login with a custom message
        return RedirectResponse(url=f"/login?message=session_expired")
    
    # Set default profile picture if none exists
    #profile_picture_url = user.profile_picture or "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"

    # Render the home.html template with user's fullname
    return templates.TemplateResponse("dashboard.html", {"request": request, "fullname": user.fullname, "user_id": user.id, "show_navbar": False})


@app.post("/logout/")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.session_token == session_token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")

    logout_user(db, user.id)
    # Clear the session cookie
    response.delete_cookie(key="session_token")
    return {"message": "Logout successful"}


@app.get("/create-article")
def create_article(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    context = {
        "request": request,
        "fullname": current_user.fullname ,
        "show_navbar": False
    }
    return templates.TemplateResponse("admin.html", context)

@app.get("/login")
@app.get("/login/")
@app.get("/admin-login")
@app.get("/admin")
def home(request: Request, message: str = Query(None), db: Session = Depends(get_db)):
    
    session_token = request.cookies.get("session_token")
    
    # If session token exists, validate it
    if session_token:
        user = db.query(User).filter(User.session_token == session_token, User.session_expiry > datetime.now()).first()
        if user:
            # Redirect to /home/{fullname} if the user is authenticated
            formatted_fullname = user.fullname.replace(" ", "-").lower()
            return RedirectResponse(url=f"/admin/{formatted_fullname}")

    # Determine the message to display on the login page
    login_message = "Veuillez vous connecter."
    if message == "not_logged_in":
        login_message = "Vous n'êtes pas connecté, veuillez vous connecter"
    elif message == "session_expired":
        login_message = "Votre session a expiré, veuillez vous reconnecter"


    return templates.TemplateResponse("admin_login.html", {"request": request, "show_navbar": False, "login_message": login_message})


@app.get("/articles")
def manage_articles(
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Query for all blog posts that belong to the current user.
    posts = db.query(BlogPost).filter(BlogPost.user_id == current_user.id).all()
    
    # Pass posts and any other context data (like fullname) to the template.
    context = {
        "request": request,
        "posts": posts,
        "fullname": current_user.fullname,
        "show_navbar": False
    }
    return templates.TemplateResponse("manage_articles.html", context)



@app.post("/admin/update-article/{post_id}")
async def update_article(
    post_id: int,
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(BlogPost).filter(BlogPost.id == post_id, BlogPost.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    
    try:
        pub_date = datetime.strptime(publication_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="📅 Date de publication invalide. Format attendu: YYYY-MM-DD")

    post.header_image=header_image,
    post.title=title,
    post.author=author,
    post.about_author=about_author,
    post.publication_date=pub_date,
    post.reading_time=reading_time,
    post.introduction=introduction,
    post.section_1_title=section_1_title,
    post.section_1_content=section_1_content,
    post.quote=quote,
    post.section_2_title=section_2_title,
    post.section_2_content=section_2_content,
    post.tools=tools,
    post.section_3_title=section_3_title,
    post.section_3_content=section_3_content,
    post.conclusion=conclusion,
    post.cta=cta,

    db.commit()
    db.refresh(post)
    return {"message": "Article mis à jour", "post_id": post.id}



@app.get("/admin/get-article/{post_id}")
def get_article(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(BlogPost).filter(BlogPost.id == post_id, BlogPost.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Return post details as JSON
    return {
        "id": post.id,
        "header_image": post.header_image,
        "title": post.title,
        "author": post.author,
        "about_author" : post.about_author,
        "publication_date": post.publication_date,
        "reading_time":post.reading_time,
        "introduction": post.introduction,
        "section_1_title": post.section_1_title,
        "section_1_content": post.section_1_content,
        "quote": post.quote,
        "section_2_title": post.section_2_title,
        "section_2_content": post.section_2_content,
        "tools": post.tools,
        "section_3_title": post.section_3_title,
        "section_3_content": post.section_3_content,
        "conclusion": post.conclusion,
        "cta": post.cta
    }



# PASSWORD UPDATE ROUTE SETTINGS

@app.post("/forgot-password/")
async def forgot_password(email: str = Form(...), db: Session = Depends(get_db)):
    result = await forgot_password_service(db=db, email=email)
    return JSONResponse(status_code=200, content={"message": result})


@app.get("/password-update/{user_id}")
def password_update_page(user_id: int, token: str, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.reset_token == token).first()
    if not user:
        return templates.TemplateResponse("verification_failed.html", {"request": request, "message": "Invalid or expired token", "show_navbar": False})
    
    return templates.TemplateResponse("password_update.html", {"request": request, "user_fullname": user.fullname, "user_id": user_id, "token": token, "show_navbar": False})


@app.post("/password-update/{user_id}")
def password_update(
    user_id: int,
    token: str,
    request: Request,
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    
    try:
        update_user_password(db, user_id, token, new_password, confirm_password)
        
        return templates.TemplateResponse(
            "password_update_success.html", {"request": request, "message": "Password updated successfully!", "show_navbar": False}
        )
    except HTTPException as e:
        return templates.TemplateResponse(
            "verification_failed.html", {"request": request, "message": str(e.detail), "show_navbar": False}
        )
















@app.exception_handler(404)
def custom_404_handler(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request, "show_navbar": False}, status_code=404, )


