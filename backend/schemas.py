from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DocumentSummary(BaseModel):
    id: int
    title: str
    source_type: str
    original_filename: str | None
    language: str
    document_type: str | None
    urgency: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentDetail(DocumentSummary):
    extracted_text: str
    sent_by: str | None
    explanation: str | None
    reason: str | None
    deadlines: str | None
    next_steps: list[str]
    contacts: str | None

    model_config = {"from_attributes": True}


class TextDocumentCreate(BaseModel):
    text: str = Field(min_length=10)
    title: str = Field(default="My Document", max_length=255)
    language: str = "english"
