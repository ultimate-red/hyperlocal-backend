# Hyperlocal Platform — Backend API

FastAPI backend for the Hyperlocal Platform. Handles user authentication (phone + OTP) and task management.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Database | SQLite (Phase 0) → PostgreSQL (production) |
| Auth | JWT tokens + OTP |
| ORM | SQLAlchemy |
| Validation | Pydantic v2 |
| Server | Uvicorn |

## Project Structure

```
hyperlocal-backend/
├── main.py          ← FastAPI app entry point, CORS config
├── config.py        ← Settings (reads from .env)
├── database.py      ← SQLAlchemy engine + session
├── models.py        ← DB models (User, Task)
├── schemas.py       ← Pydantic request/response schemas
├── auth.py          ← JWT + OTP utilities
├── routes/
│   ├── auth.py      ← /auth/request-otp, /auth/verify-otp
│   └── tasks.py     ← /tasks/ CRUD + accept/complete
├── requirements.txt
├── start.sh         ← One-command startup script
└── test_api.sh      ← curl-based API smoke tests
```

## Quick Start

```bash
# 1. Create and activate virtual environment
python3 -m venv env
source env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env   # then edit .env if needed

# 4. Start server
./start.sh
# or manually:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at **http://localhost:8000**

- Interactive API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

Copy `.env.example` to `.env` and set:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./hyperlocal.db` | DB connection string |
| `SECRET_KEY` | `dev-secret-key-...` | JWT signing key — **change in production** |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `43200` (30 days) | Token lifetime |

## API Endpoints

### Authentication

```
POST /auth/request-otp
Body: { "phone": "1234567890" }
→ Returns OTP in response (Phase 0 testing only — remove in production)

POST /auth/verify-otp
Body: { "phone": "1234567890", "otp": "123456" }
→ Returns { "access_token": "...", "token_type": "bearer", "user": {...} }
```

### Tasks (all require `Authorization: Bearer <token>`)

```
GET  /tasks/              → List all tasks
POST /tasks/              → Create task  { title, description?, reward? }
GET  /tasks/{id}          → Get task details
POST /tasks/{id}/accept   → Accept an open task
POST /tasks/{id}/complete → Mark an accepted task as completed (creator only)
```

### Utility

```
GET /          → API info
GET /health    → Health check
```

## User Flow

```
User A                          User B
  │                               │
  ├─ POST /auth/request-otp       │
  ├─ POST /auth/verify-otp        │
  ├─ POST /tasks/  (create)       │
  │                               ├─ POST /auth/request-otp
  │                               ├─ POST /auth/verify-otp
  │                               ├─ GET  /tasks/  (sees task)
  │                               ├─ POST /tasks/{id}/accept
  │                               │
  ├─ GET  /tasks/{id}  (sees accepted)
  └─ POST /tasks/{id}/complete
```

## Database

**Phase 0**: SQLite — file-based, zero setup.

```bash
# Reset database
rm hyperlocal.db
python main.py   # recreates tables on startup
```

**Production**: set `DATABASE_URL` to a PostgreSQL connection string:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

## Running Tests

```bash
# Start server first, then:
./test_api.sh
```

## Deployment (Render)

### Option A — One-click via render.yaml (recommended)

The repo includes `render.yaml` which provisions everything automatically:
- Python web service running uvicorn
- Free PostgreSQL database
- Auto-generated `SECRET_KEY`
- `DATABASE_URL` wired from the database to the service

Steps:
1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → **New** → **Blueprint**
3. Connect your GitHub repo
4. Render detects `render.yaml` and shows a preview — click **Apply**
5. Wait ~3 minutes for the first deploy

Your API will be live at `https://hyperlocal-backend.onrender.com` (or similar).

### Option B — Manual setup via Render dashboard

1. **New → Web Service** → connect your GitHub repo
   - Environment: `Python 3`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Plan: Free

2. **New → PostgreSQL** → create a free database named `hyperlocal-db`

3. In the web service **Environment** tab, add:
   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | (copy Internal Database URL from the PostgreSQL service) |
   | `SECRET_KEY` | (generate a strong random string) |
   | `ALGORITHM` | `HS256` |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `43200` |

4. **Manual Deploy** → deploy latest commit

### After deploying

Update `BASE_URL` in the Android app (`hyperlocal-android/main.py`):
```python
BASE_URL = "https://hyperlocal-backend.onrender.com"
```

> **Note**: The free Render tier spins down after 15 minutes of inactivity.
> The first request after sleep takes ~30 seconds to wake up. This is normal.

## Security Notes (Phase 0)

- OTP is returned in the API response — **remove before production**
- `SECRET_KEY` in `.env` is a placeholder — generate a strong key for production
- SQLite is not suitable for concurrent production traffic — migrate to PostgreSQL
- No rate limiting or SMS integration yet
