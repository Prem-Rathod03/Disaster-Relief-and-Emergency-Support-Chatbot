from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import re
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Disaster Relief & Emergency Support Chatbot")

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify the exact origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================= Models =======================
class Message(BaseModel):
    role: str  # "user" or "bot"
    content: str

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    response: str
    conversation_history: List[Message]

# ======================= Data Store =======================
conversations: Dict[str, List[Message]] = {}

# ======================= Disaster Resources & Tips =======================
resources = {
    "shelter": "Nearest shelter: Community Center, 123 Main St. Call 555-1234 for more info.",
    "hospital": "Nearest hospital: City Hospital, 456 Health Ave. Emergency: 911.",
    "food": "Food distribution: High School Gym, 789 School Rd. Open 9am-6pm.",
    "emergency_contact": "Emergency contact: 911 or local helpline 555-0000."
}

safety_tips = {
    "flood": "During a flood: Move to higher ground, avoid walking or driving through flood waters, and listen to local alerts.",
    "earthquake": "During an earthquake: Drop, Cover, and Hold On. Stay away from windows and heavy objects.",
    "fire": "During a fire: Evacuate immediately, stay low to avoid smoke, and call emergency services."
}

# ======================= Response Patterns =======================
default_responses = [
    "I'm not sure I understand. Could you rephrase that or ask about shelters, hospitals, food, or safety tips?",
    "I don't have an answer for that yet. Try asking about any type of disaster or emergency resources.",
    "That's interesting, but I'm not sure how to respond. You can ask for help, resources, or safety information for both natural and man-made disasters."
]

responses = {
    # Greetings
    r'hi|hello|hey': [
        "Hello! How can I assist you with disaster relief or emergency support today?",
        "Hi there! Are you in need of emergency assistance or information?",
        "Hey! How can I help you stay safe?"
    ],

    # Thanks and farewell
    r'thank you|thanks': [
        "You're welcome! Stay safe.",
        "Happy to help! If you need more information, just ask.",
        "Anytime! Let me know if you need further assistance."
    ],
    r'bye|goodbye': [
        "Goodbye! Take care and stay safe!",
        "See you later! Remember, help is always available.",
        "Bye for now! Reach out if you need more support."
    ],

    # Emergency Resources
    r'need (shelter|place to stay)': ["Nearest shelter: Community Center, 123 Main St. Call 555-1234 for more info."],
    r'nearest hospital|hospital near me': ["Nearest hospital: City Hospital, 456 Health Ave. Emergency: 911."],
    r'food (help|distribution|center)': ["Food distribution: High School Gym, 789 School Rd. Open 9am-6pm."],
    r'emergency contact|emergency number|call for help': ["Emergency contact: 911 or local helpline 555-0000."],

    # Natural Disasters
    r'flood|flood safety': [
        "During a flood: Move to higher ground, avoid walking or driving through flood waters, and listen to local alerts."
    ],
    r'earthquake|earthquake safety': [
        "During an earthquake: Drop, Cover, and Hold On. Stay away from windows and heavy objects."
    ],
    r'fire|wildfire': [
        "During a fire: Evacuate immediately, stay low to avoid smoke, and call emergency services."
    ],
    r'tsunami': [
        "Tsunami warning: Move to higher ground immediately. Stay away from the coast and listen to emergency broadcasts."
    ],
    r'hurricane|cyclone': [
        "During a hurricane: Stay indoors, secure windows, and keep emergency supplies ready."
    ],
    r'tornado': [
        "If there's a tornado: Go to a basement or small interior room without windows. Protect your head and neck."
    ],
    r'landslide': [
        "In a landslide area: Move away quickly, listen to emergency alerts, and avoid river valleys and low-lying areas."
    ],
    r'drought': [
        "During a drought: Conserve water, avoid unnecessary usage, and follow local water restrictions."
    ],
    r'heatwave|extreme heat': [
        "During a heatwave: Stay indoors during peak hours, stay hydrated, and check on vulnerable people."
    ],
    r'cold wave|blizzard|snowstorm|extreme cold': [
        "In a cold wave: Stay warm indoors, layer clothing, and avoid travel unless necessary."
    ],
    r'volcano|volcanic eruption': [
        "Volcanic eruption: Evacuate if advised, wear masks to avoid ash, and stay indoors when possible."
    ],

    # Man-made Disasters
    r'accident|road accident|car crash|vehicle accident': [
        "If you witness or are involved in an accident: Ensure your safety, call emergency services, and provide first aid if trained."
    ],
    r'chemical spill|hazardous material|toxic leak': [
        "In case of a chemical spill: Evacuate the area, avoid contact with the substance, and alert emergency services immediately."
    ],
    r'fire in building|building fire|office fire': [
        "If there's a fire in a building: Evacuate using stairs, avoid elevators, and follow the building's emergency plan."
    ],
    r'terrorism|bomb threat|explosion': [
        "In case of terrorism or bomb threat: Stay calm, follow official instructions, and move to a safe location as directed by authorities."
    ],
    r'power outage|blackout|electricity failure': [
        "During a power outage: Use flashlights, avoid using candles, and unplug electrical devices to prevent damage."
    ],
    r'gas leak|smell gas': [
        "If you smell gas: Leave the area immediately, avoid using electrical switches, and call emergency services."
    ],
    r'industrial accident|factory accident': [
        "For industrial accidents: Evacuate the area, follow safety protocols, and alert emergency response teams."
    ],
    r'building collapse|structure collapse': [
        "If a building collapses: Move away from the area, call emergency services, and help others if it is safe to do so."
    ],
    r'plane crash|aviation accident': [
        "In case of a plane crash: Alert emergency services, avoid the crash site, and help survivors if it's safe."
    ],
    r'cyber attack|data breach|hacking': [
        "In case of a cyber attack: Disconnect affected systems, report to IT or authorities, and avoid sharing sensitive data."
    ],

    # Day-to-day Disasters / Emergencies
    r'car accident|road accident|bike accident': [
        "If you're in or see a car accident, stay calm, ensure your safety, and call emergency services (911 or local helpline).",
        "Accident reported. Call for medical help immediately. If trained, offer first aid.",
        "Don't move injured persons unless there's danger (fire, traffic). Call an ambulance right away."
    ],
    r'call ambulance|need ambulance|ambulance help': [
        "Calling an ambulance: Dial 102 or your local emergency number. Stay on the line and provide details clearly.",
        "Ambulance help is on the way! Keep the injured person calm and monitor their breathing.",
        "Stay calm. Help is coming. If you know first aid, begin providing it carefully."
    ],
    r'chest pain|unconscious|not breathing|seizure|medical emergency': [
        "Medical emergency detected. Call emergency services immediately. Begin CPR if trained.",
        "Unconscious person: Check pulse and breathing. Call for medical help and follow their instructions.",
        "Seizure: Clear the area, don’t hold the person down, and time the seizure. Get medical help."
    ],
    r'bleeding|cut|injured|hurt badly': [
        "Control bleeding by applying pressure with a clean cloth. Elevate the injury and seek medical help.",
        "Apply pressure to the wound, keep the area elevated, and call emergency services if bleeding doesn't stop."
    ],
    r'fire at home|house on fire|kitchen fire': [
        "Evacuate the house immediately, alert others, and call the fire department. Do not use water on electrical or oil fires!",
        "Stay low to avoid smoke, exit the building, and don't return inside. Call for help from outside."
    ],
    r'choking|can\'t breathe|airway blocked': [
        "If someone is choking, perform the Heimlich maneuver. If unresponsive, begin CPR and call emergency services."
    ],
    r'poison|swallowed poison|chemical ingestion': [
        "Call poison control immediately. Do not induce vomiting unless instructed by professionals. Provide the substance name if possible."
    ],
    r'domestic abuse|violence at home|abuse help': [
        "You're not alone. Call a domestic abuse hotline or 911 for immediate help. Your safety is the top priority.",
        "If you're in danger, find a safe space and call emergency services or a trusted friend. Help is available."
    ],
    r'missing person|lost child|can\'t find someone': [
        "Report the missing person to the police immediately. Share last seen location and description.",
        "Time is critical. Call local authorities and alert nearby people for help."
    ],
    r'stuck in elevator|trapped in lift|elevator not moving': [
        "Stay calm and press the emergency button. Call the building help line or 911 if needed.",
        "Don't try to exit by force. Help is on the way — conserve your phone battery and stay calm."
    ]
}

# ======================= Utility =======================
def generate_bot_response(user_input: str) -> str:
    user_input = user_input.lower()
    for pattern, replies in responses.items():
        if re.search(pattern, user_input):
            return random.choice(replies)
    return random.choice(default_responses)

# ======================= Endpoints =======================
@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Disaster Relief & Emergency Support Chatbot is online!"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    user_id = req.user_id
    user_message = Message(role="user", content=req.message)
    bot_reply = generate_bot_response(req.message)
    bot_message = Message(role="bot", content=bot_reply)
    # Append to conversation history
    if user_id not in conversations:
        conversations[user_id] = []
    conversations[user_id].extend([user_message, bot_message])
    return ChatResponse(
        response=bot_reply,
        conversation_history=conversations[user_id]
    )

@app.get("/history/{user_id}", response_model=List[Message])
def get_history(user_id: str):
    if user_id not in conversations:
        raise HTTPException(status_code=404, detail="User not found")
    return conversations[user_id]

@app.post("/reset/{user_id}")
def reset_conversation(user_id: str):
    if user_id in conversations:
        conversations[user_id] = []
        return {"message": f"Conversation for user '{user_id}' has been reset."}
    else:
        return {"message": f"No conversation history found for user '{user_id}'."}

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def get_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()
