import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, Enum as SqlEnum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        UniqueConstraint("source", "channel_reference", name="uq_ticket_source_channel_ref"),
    )

    id: str = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    source: str = Column(String, nullable=False)
    channel_reference: Optional[str] = Column(String, nullable=True)
    citizen_name: Optional[str] = Column(String, nullable=True)
    contact: Optional[str] = Column(String, nullable=True)
    description: str = Column(String, nullable=False)
    location: Optional[str] = Column(String, nullable=True)
    department: Optional[str] = Column(String, nullable=True)
    status: TicketStatus = Column(SqlEnum(TicketStatus), default=TicketStatus.open, nullable=False)
    metadata_json: Optional[str] = Column("metadata", String, nullable=True)
    created_at: datetime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    attachments = relationship("Attachment", back_populates="ticket", cascade="all, delete-orphan")

    @property
    def metadata(self):
        return json.loads(self.metadata_json) if self.metadata_json else {}


class Attachment(Base):
    __tablename__ = "attachments"

    id: str = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    ticket_id: str = Column(String, ForeignKey("tickets.id"), nullable=False)
    filename: str = Column(String, nullable=False)
    url: str = Column(String, nullable=False)

    ticket = relationship("Ticket", back_populates="attachments")
