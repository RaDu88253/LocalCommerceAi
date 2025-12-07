from dotenv import load_dotenv
from datetime import timedelta
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
logger = logging.getLogger(__name__)

from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks, Form


from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from sqlalchemy.orm import Session
from .shopping_agent.graph import shopping_graph
from twilio.rest import Client as TwilioClient


# --- Local Imports ---
from .shopping_agent.graph import shopping_graph
from . import models, schemas, crud
from .database import get_db, engine, DATABASE_URL
from . import security

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Local Commerce API",
    description="An API for finding clothing from local small businesses and more."
)

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

# --- Middleware for Logging ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """A simple middleware to log incoming requests."""
    logging.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    return response


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

    # Split the response content by newlines to create a list of strings.
    # This is a safer way for the frontend to handle multi-line text.
    response_lines = final_message.content.split('\n')

    return {"response_lines": response_lines}

async def process_whatsapp_message(user_query: str, from_number: str):
    """
    This function contains the agent logic and will be run in the background.
    """
    logger.info(f"Processing background task for {from_number} with query: '{user_query}'")
    # --- Twilio Configuration ---
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not all([account_sid, auth_token, twilio_phone_number]):
        logger.error("Twilio credentials are not configured in .env file.")
        return # Stop execution if Twilio is not configured

    # Since we can't get GPS from WhatsApp, we use a default location.
    default_location = {
        "lat": 44.4268,  # Bucharest latitude
        "lng": 26.1025,  # Bucharest longitude
    }

    initial_state = {
        "user_query": user_query,
        "user_location": default_location,
        "messages": [("user", user_query)]
    }

    try:
        # Run the shopping agent graph
        final_state = await shopping_graph.ainvoke(initial_state)
        final_message = final_state["messages"][-1]
        response_text = final_message.content

        # Send the reply via Twilio
        client = TwilioClient(account_sid, auth_token)
        client.messages.create(
            from_=f'whatsapp:{twilio_phone_number}',
            body=response_text,
            to=from_number
        )
        logger.info(f"Successfully sent reply to {from_number}")
    except Exception as e:
        logger.error(f"Error processing agent or sending Twilio message for {from_number}: {e}")

@app.post("/whatsapp-webhook")
async def whatsapp_webhook(background_tasks: BackgroundTasks, Body: str = Form(...), From: str = Form(...)):
    """
    Handles incoming WhatsApp messages via Twilio webhook.
    It immediately responds to Twilio and processes the message in the background.
    """
    background_tasks.add_task(process_whatsapp_message, Body, From)

    return {} # Return an empty response immediately

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
