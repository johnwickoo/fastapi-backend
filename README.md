# FastAPI Study Logger API

A REST API for logging and tracking daily study sessions.

## Live URL
https://web-production-8e17a6.up.railway.app

## Tech Stack
- Python / FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Deployed on Railway

## Endpoints

### POST /log
Log a new study session.

Request body:
{
  "task": "string",
  "hours": int,
  "rating": int,
  "blockers": "string"
}

### GET /sessions
Returns all logged sessions.

### GET /sessions/{id}
Returns a single session by ID.

### DELETE /sessions/{id}
Deletes a session by ID.

## Run Locally
1. Clone the repo
2. Install dependencies: pip install -r requirements.txt
3. Start PostgreSQL and create a database
4. Set DATABASE_URL environment variable
5. Run: uvicorn main:app --reload