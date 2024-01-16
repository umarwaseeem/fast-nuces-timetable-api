from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pandas as pd
import re

from models import TimeTableResponseModel, TimeTableRequestModel
from utils import drop_top_rows, generate_timetable, day_names

app = FastAPI(
    title="Timetable API",
    description="Only for Fast Islamabad: API to read timetable for each subject in a convenient manner. Feel free to use in a web or mobile app.",
    docs_url="/",
)

# Enable CORS for all domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_timetable():
    return pd.ExcelFile("./timetable_spring_2024.xlsx")

# FastAPI endpoint to get all subjects
@app.get("/all-subjects", tags=["Offered Subjects"])
async def all_subjects(timetable: pd.ExcelFile = Depends(get_timetable)):
    subjects = []

    time_pattern = r'\d+:\d+-\d+:\d+' # Regular expression pattern to match time values like "1:30-2:50"

    for day in day_names:
        temp = pd.read_excel(timetable, day)
        temp = drop_top_rows(temp)
        temp = temp.iloc[:, 1:]  # Remove the first column
        temp = temp.applymap(lambda cell: re.sub(time_pattern, '', str(cell))) # Remove time values in the format "1:30-2:50" using regular expressions
        subjects.extend(temp.values.flatten())# Flatten and extend subjects

    subjects = [subject.strip() for subject in subjects if subject.strip()]# Remove empty strings and strip whitespace
    subjects = list(set(subjects))# Remove duplicates and sort
    subjects = [subject for subject in subjects if str(subject) != 'nan']# remove nan values

    return subjects

# FastAPI endpoint to get the timetable
@app.post("/time-table", response_model=List[TimeTableResponseModel], tags=["Subject Timetables"])
async def get_time_table(data: TimeTableRequestModel):
    df = generate_timetable(data.subjects)    
    timetable_json = df.to_dict(orient="records") # Convert the timetable DataFrame to JSON format
    return JSONResponse(content=timetable_json)


