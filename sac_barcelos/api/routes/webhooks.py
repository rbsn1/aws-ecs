from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_session
from ...repositories.tickets import TicketRepository
from ...schemas import MessagingPayload, TicketResponse

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def get_repository(session: Session = Depends(get_session)) -> TicketRepository:
    return TicketRepository(session)


@router.post("/telegram", response_model=TicketResponse)
def telegram_webhook(payload: MessagingPayload, repository: TicketRepository = Depends(get_repository)):
    return repository.create_from_message(payload, source="telegram")


@router.post("/whatsapp", response_model=TicketResponse)
def whatsapp_webhook(payload: MessagingPayload, repository: TicketRepository = Depends(get_repository)):
    return repository.create_from_message(payload, source="whatsapp")
