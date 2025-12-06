from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import time

# Import your models and the engine from the correct locations
import models, schemas, crud
import database

# Create the FastAPI app
app = FastAPI()

# --- Dependency ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

# --- Logging Middleware ---
# This will run for every request and print information to the console.
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    print(f"INFO:     {request.method} {request.url.path} - Completed in {formatted_process_time}ms")
    return response

# --- API Endpoints ---
# Your API routes go here. They should ideally be prefixed with /api
@app.get("/")
def get_status():
    """Root endpoint for health check."""
    return {"status": "ok"}

@app.get("/api/hello")
def read_root():
    return {"message": "Hello from the FastAPI backend!"}

@app.post("/api/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Creează un utilizator nou.
    """
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user_by_username = crud.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already taken")
        
    return crud.create_user(db=db, user=user)
