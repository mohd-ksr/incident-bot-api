import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found. Please set it in the .env file.")

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# FastAPI app
app = FastAPI()

# Request body model
class IncidentRequest(BaseModel):
    situation: str

def classify_incident(user_input: str):
    prompt = f"""
    You are an Incident Classification Bot.

    Task: Analyze the situation (which may be in English OR Hindi) 
    and return EXACTLY this format:
    Incident Priority Supplies...

    Rules:
    - Incident must be ONE word (e.g., Flood, Fire, Earthquake, Medical, Crime, Other)
    - Priority must be ONE word (High, Medium, or Low)
    - Supplies can be ONE or MORE words (space-separated), e.g., "Water Ambulance Extinguisher".
    - Do NOT add any explanation, only output the three fields.
    - Always respond in ENGLISH, even if the input is in Hindi.

    Examples:
    "A massive flood destroyed homes" → Flood High Water Boat Shelter
    "A man was injured in an accident" → Medical High Medicine Ambulance
    "Someone stole a wallet in the market" → Crime Medium Police None
    "A small fire broke out in the kitchen" → Fire High Water Extinguisher Ambulance
    "Heavy rainfall but no damage" → NaturalDisaster Low None
    "No serious issue" → Other Low None
    "मेरे घर में आग लग गई है" → Fire High Water Ambulance Extinguisher
    "एक आदमी सड़क पर गिर गया" → Medical High Ambulance Medicine

    Situation: "{user_input}"
    """
    response = model.generate_content(prompt)
    result = response.text.strip()

    parts = result.split(maxsplit=2)
    if len(parts) < 3:
        return "Other", "Low", "None"

    incident, priority, supplies = parts[0], parts[1], parts[2]
    return incident, priority, supplies

# API route
@app.post("/classify")
def classify(req: IncidentRequest):
    incident, priority, supplies = classify_incident(req.situation)
    return {
        "incident": incident,
        "priority": priority,
        "supplies": supplies
    }

@app.get("/")
def home():
    return {"message": "🚨 Incident Classification Bot API is running!"}
