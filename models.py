from pydantic import BaseModel, Field, field_validator

_TRUE = {"true", "yes", "1", "correct", "supported", "صحيح", "نعم", "حق"}
_FALSE = {"false", "no", "0", "incorrect", "unsupported", "خطأ", "لا", "باطل"}


class Verdict(BaseModel):
    statement: str = Field(description="انسخ الجملة الأصلية حرفياً")
    verdict: bool = Field(description="true إذا كانت الجملة مدعومة بالمقطع، وإلا false")

    @field_validator("verdict", mode="before")
    @classmethod
    def coerce_verdict(cls, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in _TRUE:
                return True
            if normalized in _FALSE:
                return False
        if value is None:
            return False
        raise ValueError(f"Cannot interpret verdict: {value!r}")


class Verdicts(BaseModel):
    verdicts: list[Verdict]