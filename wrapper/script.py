from pydantic import BaseModel, Field

class Script(BaseModel):
    title: str = Field(description="Title of the script")
    description: str = Field(description="Description of the script")
    content: list[str] = Field(description="Content of the script or sayings of characters in lines")
