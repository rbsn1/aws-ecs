import shutil
import uuid
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from fastapi import HTTPException, UploadFile

from ..config import get_settings
from ..schemas import AttachmentSchema

settings = get_settings()


class AttachmentService:
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or settings.attachments_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.bucket_name = settings.attachments_bucket
        self.region = settings.aws_region
        self._s3_client = None

    def _client(self):
        if self.bucket_name is None:
            return None
        if self._s3_client is None:
            self._s3_client = boto3.client("s3", region_name=self.region)
        return self._s3_client

    def save(self, file: UploadFile) -> AttachmentSchema:
        file_id = uuid.uuid4().hex
        extension = Path(file.filename or "").suffix
        local_path = self.storage_dir / f"{file_id}{extension}"

        with local_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        url = str(local_path)
        if self.bucket_name:
            client = self._client()
            object_key = f"attachments/{local_path.name}"
            try:
                client.upload_file(str(local_path), self.bucket_name, object_key)
                url = f"s3://{self.bucket_name}/{object_key}"
            except (ClientError, BotoCoreError, NoCredentialsError) as exc:
                raise HTTPException(
                    status_code=502,
                    detail=f"Falha ao enviar anexo para S3: {exc}",
                ) from exc

        return AttachmentSchema(id=file_id, filename=file.filename or local_path.name, url=url)
