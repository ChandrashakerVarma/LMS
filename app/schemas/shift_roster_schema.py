from pydantic import BaseModel

class ShiftRosterBase(BaseModel):
    name: str
    is_active: bool = True


class ShiftRosterCreate(ShiftRosterBase):
    pass


class ShiftRosterUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class ShiftRosterResponse(ShiftRosterBase):
    id: int

    model_config = {
    "from_attributes": True
}

