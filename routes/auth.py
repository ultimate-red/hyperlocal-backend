from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth import create_access_token, get_current_user_id
from config import settings
from database import get_db
from models import User
from schemas import GoogleAuthURL, Token, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def _callback_url() -> str:
    return f"{settings.app_url}/auth/google/callback"


@router.get("/google/url", response_model=GoogleAuthURL)
def google_auth_url(local_redirect: str):
    """
    Returns the Google OAuth2 authorisation URL.
    local_redirect  — where the Kivy app is listening (e.g. http://localhost:8765)
                      passed as OAuth2 'state' so the backend can forward the token there.
    """
    if not settings.google_client_id:
        raise HTTPException(status_code=500,
                            detail="GOOGLE_CLIENT_ID is not configured on the server.")
    params = {
        "client_id":     settings.google_client_id,
        "redirect_uri":  _callback_url(),
        "response_type": "code",
        "scope":         "openid email profile",
        "state":         local_redirect,
        "access_type":   "offline",
        "prompt":        "select_account",
    }
    return {"url": f"{GOOGLE_AUTH_URL}?{urlencode(params)}"}


@router.get("/google/callback")
async def google_callback(code: str, state: str, db: Session = Depends(get_db)):
    """
    Google redirects here after the user approves.
    Exchanges the code for a token, upserts the user, then redirects to
    the Kivy local server with the JWT.
    """
    # Exchange authorisation code for Google access token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "code":          code,
            "client_id":     settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri":  _callback_url(),
            "grant_type":    "authorization_code",
        })
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange Google code")
        token_data = token_resp.json()

        # Fetch user info from Google
        info_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        if info_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch Google user info")
        info = info_resp.json()

    google_id = info.get("id")
    email     = info.get("email")

    # Find or create user
    user = db.query(User).filter(User.google_id == google_id).first()
    if not user:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.google_id       = google_id
            user.profile_picture = info.get("picture")
        else:
            user = User(
                google_id       = google_id,
                email           = email,
                name            = info.get("name"),
                profile_picture = info.get("picture"),
                is_active       = True,
            )
            db.add(user)
    else:
        user.profile_picture = info.get("picture")

    db.commit()
    db.refresh(user)

    jwt_token = create_access_token({"sub": str(user.id)})

    # Forward token to the Kivy local server
    return RedirectResponse(f"{state}?token={jwt_token}&user_id={user.id}")


@router.get("/me", response_model=UserResponse)
def get_me(user_id: int = Depends(get_current_user_id),
           db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
