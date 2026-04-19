import uuid

from pydantic import BaseModel


class AuthorPayload(BaseModel):
    id: uuid.UUID

