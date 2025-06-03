from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()
# You can get a free API key from Google AI Studio: https://aistudio.google.com/
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure the generative AI library with the API key
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    # Handle the case where the API key is not found
    logging.warning("GOOGLE_API_KEY not found in .env file.")

app = FastAPI()
@app.get("/")
def root():
    return {"message": "Resume Enhancer API is working 🚀"}

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

    # Instantiate the Gemini model
    if not GOOGLE_API_KEY:
        return {"error": "API key not configured", "message": "GOOGLE_API_KEY is not set in the environment."}
        
    try:
        model = genai.GenerativeModel('gemini-pro')
    except Exception as e:
         logging.error(f"Failed to initialize Gemini model: {e}")
         return {"error": str(e), "message": "Failed to initialize Gemini model. Check API key configuration and potentially network issues."}

    prompt = f"Improve this into a strong bullet point for a {role} role:\nOriginal: {raw_input}\nImproved:"

    try:
        # Generate improved bullet point using Gemini-Pro
        response = model.generate_content(prompt)

        # Extract the generated text
        # The generated text is typically in the 'text' attribute for simple prompts.
        if response and hasattr(response, 'text'):
             bullet = response.text.strip()
        else:
             # Fallback or improved error handling if text attribute is missing
             logging.error(f"Gemini response missing text attribute or invalid format: {response}")
             bullet = "Failed to generate response or invalid response format."

        logging.info(f"Generated bullet point for '{raw_input}': {bullet}")

        return {"suggested_bullet": bullet}
    except Exception as e:
        # Log the specific error and return a generic message to the user
        logging.error(f"Failed to generate bullet point using Gemini API for input '{raw_input}': {e}")
        return {"error": str(e), "message": "Failed to generate bullet point using Gemini API."}
