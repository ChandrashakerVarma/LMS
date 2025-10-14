from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FormulaBase(BaseModel):
    component_code: str
    component_name: str
    formula_text: str
    formula_type: Optional[str] = "earning"
    is_active: Optional[bool] = True
    description: Optional[str] = None

class FormulaCreate(FormulaBase):
    pass

class FormulaUpdate(BaseModel):
    component_name: Optional[str]
    formula_text: Optional[str]
    formula_type: Optional[str]
    is_active: Optional[bool]
    description: Optional[str]

class FormulaResponse(FormulaBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FormulaBase(BaseModel):
    component_code: str
    component_name: str
    formula_text: str
    formula_type: Optional[str] = "earning"
    is_active: Optional[bool] = True
    description: Optional[str] = None

class FormulaCreate(FormulaBase):
    pass

class FormulaUpdate(BaseModel):
    component_name: Optional[str]
    formula_text: Optional[str]
    formula_type: Optional[str]
    is_active: Optional[bool]
    description: Optional[str]

class FormulaResponse(FormulaBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
