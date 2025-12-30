import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import Attachment, Ticket, TicketStatus
from ..schemas import AttachmentSchema, MessagingPayload, TicketCreate


class TicketRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self) -> List[Ticket]:
        return list(self.session.scalars(select(Ticket)).all())

    def get(self, ticket_id: str) -> Ticket:
        ticket = self.session.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Chamado não encontrado")
        return ticket

    def _persist_attachments(self, ticket: Ticket, attachments: List[AttachmentSchema]):
        for item in attachments:
            attachment = Attachment(
                id=item.id,
                filename=item.filename,
                url=item.url,
                ticket=ticket,
            )
            self.session.add(attachment)

    def _merge_metadata(self, ticket: Ticket, metadata: Dict[str, str]):
        existing_metadata = json.loads(ticket.metadata_json) if ticket.metadata_json else {}
        existing_metadata.update(metadata)
        ticket.metadata_json = json.dumps(existing_metadata, ensure_ascii=False)

    def create(
        self, ticket_data: TicketCreate, source: str, channel_reference: Optional[str] = None
    ) -> Ticket:
        now = datetime.now(timezone.utc)
        ticket = Ticket(
            source=source,
            channel_reference=channel_reference,
            citizen_name=ticket_data.citizen_name,
            contact=ticket_data.contact,
            description=ticket_data.description,
            location=ticket_data.location,
            department=ticket_data.department,
            status=TicketStatus.open,
            created_at=now,
            updated_at=now,
        )
        self.session.add(ticket)
        self.session.flush()
        self._persist_attachments(ticket, ticket_data.attachments)
        self.session.commit()
        self.session.refresh(ticket)
        return ticket

    def create_from_message(self, payload: MessagingPayload, source: str) -> Ticket:
        attachments = [
            AttachmentSchema(
                id=item.filename or payload.message_id or payload.chat_id,
                filename=item.filename or item.url,
                url=str(item.url),
            )
            for item in payload.attachments
        ]
        ticket_payload = TicketCreate(
            citizen_name=payload.citizen_name,
            contact=payload.contact or payload.chat_id,
            description=payload.text,
            location=payload.location,
            attachments=attachments,
        )
        try:
            return self.create(ticket_payload, source=source, channel_reference=payload.message_id or payload.chat_id)
        except IntegrityError:
            self.session.rollback()
            existing = (
                self.session.scalars(
                    select(Ticket).where(
                        Ticket.source == source,
                        Ticket.channel_reference == (payload.message_id or payload.chat_id),
                    )
                )
                .first()
            )
            if existing:
                return existing
            raise

    def update_assignment(self, ticket_id: str, department: str) -> Ticket:
        ticket = self.get(ticket_id)
        ticket.department = department
        ticket.updated_at = datetime.now(timezone.utc)
        self.session.commit()
        self.session.refresh(ticket)
        return ticket

    def update_status(self, ticket_id: str, status: TicketStatus, metadata: Dict[str, str]) -> Ticket:
        ticket = self.get(ticket_id)
        ticket.status = status
        ticket.updated_at = datetime.now(timezone.utc)
        self._merge_metadata(ticket, metadata)
        self.session.commit()
        self.session.refresh(ticket)
        return ticket
