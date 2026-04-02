# FastAPI Session Logger

This is a small FastAPI app for recording study or work sessions and reading them back later.

## Endpoints

### `POST /log`

This endpoint saves a new session to `sessions.txt`.

Send a JSON body with:

- `task`: the name of the task you worked on
- `hours`: how many hours you spent
- `rating`: a score for how the session went

Example request:

```json
{
  "task": "Build API routes",
  "hours": 2,
  "rating": 5
}
```

Example response:

```json
{
  "message": "Session logged",
  "data": {
    "task": "Build API routes",
    "hours": 2,
    "rating": 5
  }
}
```

### `GET /sessions`

This endpoint reads all saved sessions from `sessions.txt` and returns them as a list.

If no sessions have been logged yet, it returns an empty list.

Example response:

```json
{
  "sessions": [
    {
      "task": "Build API routes",
      "hours": 2,
      "rating": 5
    }
  ]
}
```

