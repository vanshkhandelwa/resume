from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import cohere
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()
# Get API key from .env file
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Configure the Cohere client
if COHERE_API_KEY:
    co = cohere.Client(COHERE_API_KEY)
else:
    logging.warning("COHERE_API_KEY not found in .env file.")
    co = None # Set co to None if key is missing

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/suggest-bullets")
async def suggest_bullets(request: Request):
    data = await request.json()
    raw_input = data["text"]
    role = data.get("role", "general")

    # Check if Cohere client is configured
    if not co:
         return {"error": "API key not configured", "message": "COHERE_API_KEY is not set in the environment."}

    prompt = f"Improve this into a strong bullet point for a {role} role:\nOriginal: {raw_input}\nImproved:"

    try:
        # Generate improved bullet point using Cohere
        # Using a good model like command-r-plus or command is recommended for quality
        # Check Cohere documentation for available models and parameters
        response = co.generate(
            prompt=prompt,
            model='command', # You can try 'command-r-plus' or other models if available/suitable
            max_tokens=100, # Adjust as needed
            temperature=0.7,
            num_generations=1
        )

        # Extract the generated text from Cohere response
        if response and response.generations:
             bullet = response.generations[0].text.strip()
        else:
             logging.error(f"Cohere response missing generations or text: {response}")
             bullet = "Failed to generate response or invalid response format."

        logging.info(f"Generated bullet point for '{raw_input}': {bullet}")

        return {"suggested_bullet": bullet}
    except Exception as e:
        # Log the specific error
        logging.error(f"Failed to generate bullet point using Cohere API for input '{raw_input}': {e}")
        return {"error": str(e), "message": "Failed to generate bullet point using Cohere API."}
