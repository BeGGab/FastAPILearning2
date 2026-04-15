import uuid

from pydantic import BaseModel


class AuthorPayload(BaseModel):
    id: uuid.UUID



class UserPayload(BaseModel):
    id: uuid.UUID

class StudentPayload(BaseModel):
    id: uuid.UUID