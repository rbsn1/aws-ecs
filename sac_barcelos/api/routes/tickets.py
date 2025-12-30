from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_session
from ...repositories.tickets import TicketRepository
from ...schemas import AssignmentUpdate, StatusUpdate, TicketCreate, TicketResponse

router = APIRouter(prefix="/tickets", tags=["tickets"])


def get_repository(session: Session = Depends(get_session)) -> TicketRepository:
    return TicketRepository(session)


@router.post("", response_model=TicketResponse)
def create_ticket(payload: TicketCreate, repository: TicketRepository = Depends(get_repository)):
    return repository.create(ticket_data=payload, source="backoffice")


@router.get("", response_model=List[TicketResponse])
def list_tickets(repository: TicketRepository = Depends(get_repository)):
    return repository.list()


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str, repository: TicketRepository = Depends(get_repository)):
    return repository.get(ticket_id)


@router.patch("/{ticket_id}/assignment", response_model=TicketResponse)
def update_assignment(
    ticket_id: str, payload: AssignmentUpdate, repository: TicketRepository = Depends(get_repository)
):
    return repository.update_assignment(ticket_id=ticket_id, department=payload.department)


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_status(
    ticket_id: str, payload: StatusUpdate, repository: TicketRepository = Depends(get_repository)
):
    return repository.update_status(ticket_id=ticket_id, status=payload.status, metadata=payload.metadata)
