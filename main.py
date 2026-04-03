from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

DATABASE_URL = "postgresql://admin@localhost/studylogger"

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

Base.metadata.create_all(bind=engine)

app = FastAPI()

class SessionInput(BaseModel):
    task: str
    hours: int
    rating: int
    blockers: str = "none"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
