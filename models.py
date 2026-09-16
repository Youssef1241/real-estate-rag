from pydantic import BaseModel

class Statement(BaseModel):
    statement: str
    source: str

class Statements(BaseModel):
    statements: list[Statement]