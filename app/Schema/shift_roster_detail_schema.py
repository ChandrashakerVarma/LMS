from pydantic import BaseModel
from typing import Optional

class ShiftRosterDetailCreate(BaseModel):
    shift_roster_id: int
    week_day_id: int
    shift_id: int


class ShiftRosterDetailUpdate(BaseModel):
    week_day_id: Optional[int] = None
    shift_id: Optional[int] = None


class ShiftRosterDetailResponse(BaseModel):
    id: int
    shift_roster_id: int
    week_day_id: int
    shift_id: int

    model_config = {
    "from_attributes": True
}

