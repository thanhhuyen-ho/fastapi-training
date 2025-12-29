import os
from dotenv import load_dotenv
import httpx
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2
from sqlalchemy.orm import Session
from models import User
from operations import get_user
from db_connection import get_session

load_dotenv()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")
GITHUB_AUTHORIZATION_URL = os.getenv("GITHUB_AUTHORIZATION_URL")

def resolve_github_token(
    access_token: str = Depends(OAuth2()),
    session: Session = Depends(get_session),
) -> User:
    user_response = httpx.get(
        "https://api.github.com/user",
    headers={"Authorization": access_token},
    ).json()
    username = user_response.get("login", " ")
    user = get_user(session, username)
    if not user:
        email = user_response.get("email", " ")
        user = get_user(session, email)
    # Process user_response
    # to log the user in or create a new account
    if not user:
        raise HTTPException(
            status_code=403, detail="Token not valid"
        ) 
    return user