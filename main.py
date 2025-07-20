from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# Database setup
DATABASE_URL = "sqlite:///./assignment_tracker.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Secret key for JWT
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="EdTech Assignment Tracker", description="API for managing assignments and submissions in an EdTech platform", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Create submissions directory if not exists
os.makedirs("submissions", exist_ok=True)

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String)
    submitted_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Schemas
class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class AssignmentCreate(BaseModel):
    title: str
    description: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Utility functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: SessionLocal = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/signup", status_code=201, summary="User Signup", description="Create a new user account as student or teacher")
def signup(user: UserCreate, db: SessionLocal = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User(username=user.username, password=user.password, role=user.role)
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

@app.post("/login", response_model=Token, summary="User Login", description="Authenticate user and return JWT token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username, User.password == form_data.password).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/assignments/create", summary="Create Assignment", description="Teachers can create assignments")
def create_assignment(assignment: AssignmentCreate, current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create assignments")
    new_assignment = Assignment(title=assignment.title, description=assignment.description, created_by=current_user.id)
    db.add(new_assignment)
    db.commit()
    return {"message": "Assignment created"}

@app.post("/assignments/{assignment_id}/submit", summary="Submit Assignment", description="Students can submit assignment files")
def submit_assignment(assignment_id: int, file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit assignments")
    file_location = f"submissions/assignment_{assignment_id}_student_{current_user.id}_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    new_submission = Submission(assignment_id=assignment_id, student_id=current_user.id, file_path=file_location)
    db.add(new_submission)
    db.commit()
    return {"message": "Submission successful", "file_path": file_location}

@app.get("/assignments/{assignment_id}/submissions", summary="View Submissions", description="Teachers can view all submissions for an assignment")
def view_submissions(assignment_id: int, current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view submissions")
    submissions = db.query(Submission).filter(Submission.assignment_id == assignment_id).all()
    result = [{"student_id": s.student_id, "file_path": s.file_path, "submitted_at": s.submitted_at} for s in submissions]
    return result

@app.get("/", summary="Root API", description="Health check endpoint")
def read_root():
    return {"message": "EdTech Assignment Tracker API is running"}

# Custom OpenAPI Schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="EdTech Assignment Tracker API",
        version="1.0.0",
        description="API endpoints for managing users, assignments, and submissions",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
