"""
NUJJUM Database Schemas

Each Pydantic model maps to a MongoDB collection named after the class in lowercase.
Example: class PodUser -> collection "poduser"
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class DisabilityProfile(BaseModel):
    disability_type: List[Literal["visual", "hearing", "mobility", "cognitive", "multiple"]] = Field(..., description="Primary disability categories")
    preferred_mode: Literal["voice", "text", "simplified", "auto"] = "auto"
    language: Literal["en", "ar"] = "en"
    high_contrast: bool = False
    large_text: bool = False

class PodUser(BaseModel):
    name: Optional[str] = Field(None, description="Full name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    country: Optional[str] = None
    city: Optional[str] = None
    profile: DisabilityProfile
    documents_submitted: List[str] = []

class Sos(BaseModel):
    user_id: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    emergency_type: Literal["medical", "safety", "mobility_support", "other"] = "medical"
    status: Literal["open", "closed"] = "open"
