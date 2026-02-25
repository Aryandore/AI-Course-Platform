from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=50)

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True