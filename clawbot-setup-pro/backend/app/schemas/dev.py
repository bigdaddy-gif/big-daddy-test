from pydantic import BaseModel, EmailStr


class DevLoginRequest(BaseModel):
    email: EmailStr
