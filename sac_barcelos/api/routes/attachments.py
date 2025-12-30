from typing import List

from fastapi import APIRouter, Depends, File, UploadFile

from ...services.attachments import AttachmentService
from ...schemas import AttachmentSchema

router = APIRouter(prefix="/attachments", tags=["attachments"])


def get_attachment_service() -> AttachmentService:
    return AttachmentService()


@router.post("", response_model=List[AttachmentSchema])
async def upload_attachments(
    files: List[UploadFile] = File(...), service: AttachmentService = Depends(get_attachment_service)
):
    return [service.save(file) for file in files]
