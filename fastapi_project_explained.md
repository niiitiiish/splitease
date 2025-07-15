# FastAPI Project Explained (Beginner Friendly)

## Overview
This project is a simple web app using FastAPI and PostgreSQL. It lets users register and log in, and stores user data in a database.

---

## 1. `database.py`
Sets up the connection to your PostgreSQL database and prepares SQLAlchemy tools.

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:car24@localhost:5432/splitease"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```
- **create_engine**: Connects Python to your database.
- **declarative_base**: Lets you define tables as Python classes.
- **sessionmaker**: Lets you create sessions (connections) to the database.
- **SQLALCHEMY_DATABASE_URL**: Connection string for your database.
- **engine**: The actual connection to the database.
- **SessionLocal**: Function to create new sessions.
- **Base**: Base class for all your tables.

---

## 2. `models.py`
Defines what your database tables look like using Python classes.

```python
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
```
- **User**: Table called `users` with columns:
  - `id`: Integer, primary key, indexed.
  - `username`: String, unique, not empty.
  - `password`: String, not empty.

---

## 3. `schemas.py`
Defines what data should look like when it comes in or goes out of your API, using Pydantic models.

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
```
- **UserCreate**: Data needed to create a user (username and password).

---

## 4. `main.py`
Runs your FastAPI app and connects everything together.

```python
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import schemas
from database import SessionLocal, engine, Base
import models

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "Welcome to SplitEase!"})

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = models.User(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered", "user_id": new_user.id}

@app.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not existing_user or existing_user.password != user.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"message": "Login successful"}
```

- **Base.metadata.create_all(bind=engine)**: Creates tables if they don't exist.
- **app = FastAPI()**: Starts your app.
- **templates**: For HTML pages.
- **app.mount**: For static files (images, CSS, etc).
- **get_db()**: Gives you a database session for each request.
- **@app.get("/")**: Homepage route.
- **@app.post("/register")**: Register a new user.
- **@app.post("/login")**: Log in a user.

---

## 5. Folders
- **static/**: For images, CSS, icons, etc.
- **templates/**: For HTML files (like `index.html`).

---

## How Everything Connects

```mermaid
graph TD
    A[User] -->|POST /register| B[FastAPI App]
    A -->|POST /login| B
    B -->|uses| C[models.py]
    B -->|uses| D[schemas.py]
    B -->|uses| E[database.py]
    B -->|renders| F[templates/index.html]
    B -->|serves| G[static/]
```

---

## How to Test
- Start your app: `uvicorn main:app --reload`
- Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to use the interactive API docs.
- Register and log in users using the `/register` and `/login` endpoints.

---

## Summary
- **database.py**: Sets up the database connection and tools.
- **models.py**: Defines your database tables.
- **schemas.py**: Defines what data looks like for your API.
- **main.py**: Runs your app and connects everything together.
- **static/** and **templates/**: For your website's files and pages.

If you want to add more features or need more explanations, just ask! 