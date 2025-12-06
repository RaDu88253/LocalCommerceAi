from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import time

# Import your models and the engine from the correct locations
from app import models
from .database import engine

# Create the FastAPI app
app = FastAPI()

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
