from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class MenuBase(BaseModel):
    name: str
    display_name: str
    route: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    menu_order: Optional[int] = 0
    is_active: Optional[bool] = True

class MenuCreate(MenuBase):
    pass

class MenuUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    route: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    menu_order: Optional[int] = None
    is_active: Optional[bool] = None

class MenuResponse(MenuBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    model_config = {"from_attributes": True}

class MenuTreeResponse(MenuResponse):
    children: List["MenuTreeResponse"] = Field(default_factory=list)
    model_config = {"from_attributes": True}

# Use model_rebuild() instead of update_forward_refs()
MenuTreeResponse.model_rebuild()
