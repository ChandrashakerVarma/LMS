from pydantic import BaseModel




class TestReportCreate(BaseModel):
    module_name: str
    total_tests: int
    passed: int
    failed: int