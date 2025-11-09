from pydantic import BaseModel

class ShiftRosterDetailBase(BaseModel):
    shift_roster_id: int
    week_day_id: int
    shift_id: int


class ShiftRosterDetailCreate(ShiftRosterDetailBase):
    pass


class ShiftRosterDetailResponse(ShiftRosterDetailBase):
    id: int

    class Config:
        orm_mode = True
