# import os
# import google.generativeai as genai
# from dotenv import load_dotenv
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel

# # Load environment variables
# load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")

# if not api_key:
#     raise ValueError("❌ GEMINI_API_KEY not found. Please set it in the .env file.")

# # Configure Gemini
# genai.configure(api_key=api_key)

# # ✅ Use a currently supported model name
# # 'gemini-2.0-flash' and 'gemini-1.5-pro' are valid as of Oct 2025
# MODEL_NAME = "gemini-2.0-flash"
# model = genai.GenerativeModel(MODEL_NAME)

# # FastAPI app
# app = FastAPI()

# # ✅ Enable CORS so frontend can call API
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # you can restrict to ["http://localhost:5500"] later
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Request body model
# class IncidentRequest(BaseModel):
#     situation: str


# def classify_incident(user_input: str):
#     prompt = f"""
#     You are an Incident Classification Bot.

#     Task: Analyze the situation (which may be in English OR Hindi) 
#     and return EXACTLY this format:
#     Incident Priority Supplies...

#     Rules:
#     - Incident must be ONE word (e.g., Flood, Fire, Accident, Earthquake, Medical, Crime, Other)
#     - Priority must be ONE word (High, Medium, or Low)
#     - Supplies can be ONE or MORE words (space-separated), e.g., "Water Ambulance Extinguisher".
#     - Do NOT add any explanation, only output the three fields.
#     - Always respond in ENGLISH, even if the input is in Hindi or any other language.

#     Examples:
#     "A massive flood destroyed homes" → Flood High Water Boat Shelter
#     "A man was injured in an accident" → Medical High Medicine Ambulance
#     "Someone stole a wallet in the market" → Crime Medium Police None
#     "A small fire broke out in the kitchen" → Fire High Water Extinguisher Ambulance
#     "Heavy rainfall but no damage" → NaturalDisaster Low None
#     "No serious issue" → Other Low None
#     "मेरे घर में आग लग गई है" → Fire High Water Ambulance Extinguisher
#     "एक आदमी सड़क पर गिर गया" → Medical High Ambulance Medicine

#     Situation: "{user_input}"
#     """

#     try:
#         response = model.generate_content(prompt)
#         result = response.text.strip()
#     except Exception as e:
#         print("❌ Error from Gemini API:", e)
#         return "Other", "Low", "None"

#     # Parse model response safely
#     parts = result.split(maxsplit=2)
#     if len(parts) < 3:
#         return "Other", "Low", "None"

#     incident, priority, supplies = parts[0], parts[1], parts[2]
#     return incident.capitalize(), priority.capitalize(), supplies.title()


# # API route
# @app.post("/classify")
# def classify(req: IncidentRequest):
#     incident, priority, supplies = classify_incident(req.situation)
#     return {
#         "incident": incident,
#         "priority": priority,
#         "supplies": supplies
#     }


# @app.get("/")
# def home():
#     return {"message": f"🚨 Incident Classification Bot API is running with {MODEL_NAME}!"}






import os
from groq import Groq
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("❌ GROQ_API_KEY not found. Please set it in the .env file.")

# Configure Groq client
client = Groq(api_key=api_key)
MODEL_NAME = "llama-3.1-8b-instant"

# FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class IncidentRequest(BaseModel):
    situation: str


def classify_incident(user_input: str):
    prompt = f"""
You are an Incident Classification Bot.

Task: Analyze the situation (which may be in English OR Hindi)
and return EXACTLY this format:
Incident Priority Supplies

Rules:
- Incident must be ONE word (Flood, Fire, Accident, Earthquake, Medical, Crime, Other, NaturalDisaster)
- Priority must be ONE word (High, Medium, Low)
- Supplies can be ONE or MORE words (space-separated)
- Do NOT add any explanation
- Always respond in ENGLISH

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

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict format classifier. Output only three fields."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        result = response.choices[0].message.content.strip()

    except Exception as e:
        print("❌ Error from Groq API:", e)
        return "Other", "Low", "None"

    parts = result.split(maxsplit=2)
    if len(parts) < 3:
        return "Other", "Low", "None"

    incident, priority, supplies = parts[0], parts[1], parts[2]
    return incident.capitalize(), priority.capitalize(), supplies.title()


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
    return {"message": f"🚨 Incident Classification Bot API is running with {MODEL_NAME} via Groq!"}