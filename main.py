import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "input your own secret key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://admin@localhost/studylogger")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

security = HTTPBearer(auto_error=False)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class SessionLog(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    task = Column(String)
    hours = Column(Integer)
    rating = Column(Integer)
    blockers = Column(String, default="none")
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()

class SessionInput(BaseModel):
    task: str
    hours: int
    rating: int
    blockers: str = "none"

class UserCreate(BaseModel):
    username: str
    password: str
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="No token provided")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/log")
def log_session(session: SessionInput, db: Session = Depends(get_db)):
    entry = SessionLog(**session.dict())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@app.get("/sessions")
def get_sessions(db: Session = Depends(get_db)):
    return db.query(SessionLog).all()

@app.get("/sessions/{id}")
def get_sessions_byId(id: int, db: Session = Depends(get_db)):
    entry = db.query(SessionLog).filter(SessionLog.id ==id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Session not found")
    return(entry)

@app.delete("/sessions/{id}")
def delete_session_byId(id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    entry = db.query(SessionLog).filter(SessionLog.id == id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(entry)
    db.commit()
    return {"message": f"Session {id} deleted by {current_user.username}"}

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = pwd_context.hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"User {user.username} created"}

@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token_data = {"sub": db_user.username}
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data.update({"exp": expire})
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}