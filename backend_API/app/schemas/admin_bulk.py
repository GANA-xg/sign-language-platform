import uuid
from typing import List
from pydantic import BaseModel


class BulkUserActionRequest(BaseModel):
    user_ids: List[uuid.UUID]
    action: str  # "activate" or "deactivate"


class BulkUserActionResponse(BaseModel):
    updated_count: int
    failed_ids: List[uuid.UUID]


class BulkLessonUploadResult(BaseModel):
    created_count: int
    failed_rows: List[dict]