from pydantic import BaseModel, Field


class TeacherDTO(BaseModel):
    name: str = Field(
        ..., description="First and second name of teacher assistant"
    )
    group: str = Field(..., description="Group of a teacher assistant")
