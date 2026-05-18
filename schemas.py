from pydantic import BaseModel, Field, ConfigDict

# User Registration
class UserCreate(BaseModel):
    username: str = Field(min_length=6, max_length=20, pattern=r"^[a-zA-Z0-9]+$", description="Enter your username")
    password: str = Field(min_length=8, max_length=72, description="Enter your password")

# User Login
class UserLogin(BaseModel):
    username: str
    password: str

# Return User Response
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str

# Authentication Response
class Token(BaseModel):
    access_token: str
    token_type : str = "bearer"

# Portfolio Creation
class PortfolioCreate(BaseModel):
    name: str = Field(min_length=2, max_length=40, description="Enter your portfolio name")

# Portfolio Creation Response
class PortfolioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str