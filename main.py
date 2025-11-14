import os
from typing import List, Optional, Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from database import create_document, get_documents

app = FastAPI(title="NUJJUM API", description="Adaptive accessibility platform for Persons of Determination (POD)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DisabilityProfile(BaseModel):
    disability_type: List[Literal["visual", "hearing", "mobility", "cognitive", "multiple"]] = Field(..., description="Primary disability categories")
    preferred_mode: Literal["voice", "text", "simplified", "auto"] = "auto"
    language: Literal["en", "ar"] = "en"
    high_contrast: bool = False
    large_text: bool = False


class UserProfile(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    profile: DisabilityProfile
    documents_submitted: List[str] = []


class ProfileCreateRequest(BaseModel):
    user: UserProfile


class ProfileCreateResponse(BaseModel):
    id: str
    message: str


class SOSRequest(BaseModel):
    user_id: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    emergency_type: Literal["medical", "safety", "mobility_support", "other"] = "medical"


class SOSResponse(BaseModel):
    id: str
    status: str
    message: str


@app.get("/")
def read_root():
    return {"message": "NUJJUM Backend is running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the NUJJUM backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, 'name', "✅ Connected")
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# Localization - minimal core strings for EN and AR
TRANSLATIONS = {
    "en": {
        "title": "NUJJUM — Accessibility & Empowerment",
        "subtitle": "Adaptive hub for health, benefits, community and emergency support",
        "get_started": "Get Started",
        "save": "Save",
        "sos": "Emergency SOS",
        "healthcare": "Healthcare",
        "benefits": "Government Benefits",
        "community": "Community",
        "devices": "Assistive Devices",
        "education": "Education & Employment",
        "global": "Global Requests",
        "voice_mode": "Voice Mode",
        "text_mode": "Text Mode",
        "simplified_mode": "Simplified Mode",
        "high_contrast": "High Contrast",
        "large_text": "Large Text",
        "language": "Language",
        "profile_saved": "Profile saved successfully"
    },
    "ar": {
        "title": "نُجُّوم — منصة الوصول والتمكين",
        "subtitle": "واجهة تكيفية للصحة والمزايا والمجتمع والدعم الطارئ",
        "get_started": "ابدأ",
        "save": "حفظ",
        "sos": "نداء طارئ",
        "healthcare": "الرعاية الصحية",
        "benefits": "المزايا الحكومية",
        "community": "المجتمع",
        "devices": "الأجهزة المساعدة",
        "education": "التعليم والعمل",
        "global": "الطلبات العالمية",
        "voice_mode": "وضع الصوت",
        "text_mode": "وضع النص",
        "simplified_mode": "وضع مبسط",
        "high_contrast": "تباين عالٍ",
        "large_text": "نص كبير",
        "language": "اللغة",
        "profile_saved": "تم حفظ الملف الشخصي بنجاح"
    },
}


@app.get("/api/i18n/{lang}")
def get_translations(lang: str):
    lang = "ar" if lang.lower().startswith("ar") else "en"
    return TRANSLATIONS[lang]


# Profiles
@app.post("/api/profile", response_model=ProfileCreateResponse)
def create_profile(payload: ProfileCreateRequest):
    try:
        data = payload.user.model_dump()
        profile_id = create_document("poduser", data)
        return ProfileCreateResponse(id=profile_id, message="Profile created")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/profile")
def list_profiles(limit: int = 10):
    try:
        docs = get_documents("poduser", {}, limit)
        # sanitize ObjectId
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Services catalog (static seed for MVP)
@app.get("/api/services")
def get_services():
    return {
        "categories": [
            {"key": "healthcare", "name": "Healthcare", "items": [
                {"name": "Telemedicine", "description": "Virtual consults with accessibility options"},
                {"name": "Rehabilitation", "description": "Physio, speech, occupational therapy"}
            ]},
            {"key": "benefits", "name": "Government Benefits", "items": [
                {"name": "POD ID Verification", "description": "Submit documents to unlock programs"},
                {"name": "Subsidies", "description": "Travel, devices, healthcare subsidies"}
            ]},
            {"key": "community", "name": "Community", "items": [
                {"name": "Local Groups", "description": "Meetups and support circles"},
                {"name": "Volunteers", "description": "Request helpers and guides"}
            ]},
            {"key": "devices", "name": "Assistive Devices", "items": [
                {"name": "Marketplace", "description": "Screen readers, hearing aids, mobility aids"}
            ]},
            {"key": "education", "name": "Education & Employment", "items": [
                {"name": "Accessible Courses", "description": "Learning paths with captions and TTS"},
                {"name": "Inclusive Jobs", "description": "Listings with accommodations"}
            ]},
            {"key": "global", "name": "Global Requests", "items": [
                {"name": "Cross-border Support", "description": "Travel and relocation assistance"}
            ]}
        ]
    }


# SOS
@app.post("/api/sos", response_model=SOSResponse)
def create_sos(req: SOSRequest):
    try:
        data = req.model_dump()
        data["status"] = "open"
        sos_id = create_document("sos", data)
        return SOSResponse(id=sos_id, status="open", message="SOS logged. Coordinators notified.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
