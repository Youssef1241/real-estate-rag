from pydantic import BaseModel, Field


class Statement(BaseModel):
    statement: str = Field(description="جملة الإجابة بالعربية الفصحى")
    source: str = Field(description="معرف المقطع ID")


class Statements(BaseModel):
    statements: list[Statement]