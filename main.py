from fastapi import FastAPI
from pydantic import BaseModel
import json

app = FastAPI()

class Session(BaseModel):
    task: str
    hours: int
    rating: int


@app.post("/log")
def log_session(session: Session):
    with open("sessions.txt", "a") as f:
        f.write(json.dumps(session.dict()) + "\n")
    return {"message": "Session logged", "data": session}

@app.get("/sessions")
def get_sessions():
    sessions = []
    try:
        with open("sessions.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    sessions.append(json.loads(line))
    except FileNotFoundError:
        return {"sessions": []}
    return {"sessions": sessions}