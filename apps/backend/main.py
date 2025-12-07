from dotenv import load_dotenv
import os
import logging

# --- Environment Variable Loading ---
# Build a path to the .env file relative to this file's location (backend/.env)
# This makes the app runnable from any directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Logging Configuration ---
# This ensures that print statements and logs are visible in the uvicorn console.
logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .shopping_agent.graph import shopping_graph

app = FastAPI(
    title="Local Commerce API",
    description="An API for finding clothing from local small businesses and more."
    )
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

# --- Database Initialization ---
# Import your models and the engine from the correct locations
from . import models, schemas, crud
from .database import get_db, engine, DATABASE_URL

from . import security

# --- CORS Middleware ---
# This must be placed before any routes

origins = [
    "*"  # Allow all origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


class ShoppingRequest(BaseModel):
    """The request model for the shopping assistant."""
    user_query: str
    latitude: float
    longitude: float

@app.post("/shopping-assistant")
async def run_shopping_assistant(request: ShoppingRequest):
    """
    Runs the shopping assistant graph based on user query and location.
    """
    initial_state = {
        "user_query": request.user_query,
        "user_location": {"lat": request.latitude, "lng": request.longitude},
        "messages": [("user", request.user_query)]
    }

    final_state = await shopping_graph.ainvoke(initial_state)
    final_message = final_state["messages"][-1]

    return {"response": final_message.content}

@app.get("/api/hello")
def read_root():
    return {"message": "Hello from the FastAPI backend!"}

@app.get("/api/status")
def read_root():
    """A simple endpoint to check if the API is running."""
    return {"status": "ok"}

@app.post("/api/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Creează un utilizator nou.
    """
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Add a check for the phone number
    db_user_by_phone = db.query(models.User).filter(models.User.phone_number == user.phone_number).first()
    if db_user_by_phone:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    return crud.create_user(db=db, user=user)

@app.post("/api/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Autentifică utilizatorul și returnează un token de acces.
    """
    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(security.get_current_user)):
    """
    Endpoint protejat care returnează datele utilizatorului curent.
    """
    return current_user
