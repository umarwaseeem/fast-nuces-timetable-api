from typing import List
from pydantic import BaseModel

class TimeTableRequestModel(BaseModel):
    subjects: List[str] = ["Subject Name"]

class TimeTableResponseModel(BaseModel):
    subject: str = "OS (CS-G)"
    room: str = "C-404"
    start_time: str = "10:00"
    end_time: str = "11:20"
    day: str = "Monday"