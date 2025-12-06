from dotenv import load_dotenv
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from shopping_agent.graph import shopping_graph

# Load environment variables from .env file at the start
load_dotenv()

app = FastAPI(
    title="Local Commerce API",
    description="An API for finding clothing from local small businesses and more."
)

# Add CORS middleware for hackathon-friendly development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class ShoppingRequest(BaseModel):
    """The request model for the shopping assistant."""
    user_query: str
    user_location: str

@app.post("/shopping-assistant")
async def run_shopping_assistant(request: ShoppingRequest):
    """
    Runs the shopping assistant graph based on user query and location.
    """
    initial_state = {
        "user_query": request.user_query,
        "user_location": request.user_location,
        "messages": [("user", request.user_query)]
    }

    final_state = await shopping_graph.ainvoke(initial_state)
    final_message = final_state["messages"][-1]

    return {"response": final_message.content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
