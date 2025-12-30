from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl

from .models import TicketStatus


class AttachmentSchema(BaseModel):
    id: str
    filename: str
    url: str

    class Config:
        orm_mode = True


class TicketBase(BaseModel):
    citizen_name: Optional[str] = None
    contact: Optional[str] = None
    description: str
    location: Optional[str] = None
    department: Optional[str] = None


class TicketCreate(TicketBase):
    attachments: List[AttachmentSchema] = Field(default_factory=list)


class TicketResponse(TicketBase):
    id: str
    source: str
    channel_reference: Optional[str] = None
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
    attachments: List[AttachmentSchema] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)

    class Config:
        orm_mode = True


class AssignmentUpdate(BaseModel):
    department: str = Field(description="Departamento responsável pelo chamado")


class StatusUpdate(BaseModel):
    status: TicketStatus
    metadata: Dict[str, str] = Field(default_factory=dict)


class MessagingAttachment(BaseModel):
    url: HttpUrl
    filename: Optional[str] = None


class MessagingPayload(BaseModel):
    chat_id: str
    citizen_name: Optional[str] = None
    contact: Optional[str] = None
    text: str
    location: Optional[str] = None
    attachments: List[MessagingAttachment] = Field(default_factory=list)
    message_id: Optional[str] = Field(default=None, description="Identificador da mensagem no provedor")
