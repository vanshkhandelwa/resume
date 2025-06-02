from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
# You can get a free API key from Google AI Studio: https://aistudio.google.com/
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure the generative AI library with the API key
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    # Handle the case where the API key is not found
    # You might want to log an error or raise an exception here in a real application
    print("Warning: GOOGLE_API_KEY not found in .env file.")

app = FastAPI()

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
    try:
        model = genai.GenerativeModel('gemini-pro')
    except Exception as e:
         return {"error": str(e), "message": "Failed to initialize Gemini model. Check API key configuration."}

    prompt = f"Improve this into a strong bullet point for a {role} role:\nOriginal: {raw_input}\nImproved:"

    try:
        # Generate improved bullet point using Gemini-Pro
        response = model.generate_content(prompt)
        
        # Extract the generated text
        # Gemini API response structure might vary, access .text attribute for instance for simple text generation
        if response and hasattr(response, 'text'):
             bullet = response.text.strip()
        else:
             bullet = "Failed to generate response or invalid response format."
        
        return {"suggested_bullet": bullet}
    except Exception as e:
        # More specific error handling could be added based on Gemini API error types
        return {"error": str(e), "message": "Failed to generate bullet point using Gemini API."}
