from pydantic import BaseModel, Field, ConfigDict

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str

class UserCreate(BaseModel):
    username: str = Field(min_length=6, max_length=20, pattern=r"^[a-zA-Z0-9]+$", description="Enter your username")
    password: str = Field(min_length=8, max_length=72, description="Enter your password")

