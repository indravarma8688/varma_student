import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import os

app = FastAPI()

DATA_FILE = "students.json"


class Student(BaseModel):
    id: int
    name: str
    age: int
    grade: str
    email: Optional[str] = None


def load_students() -> Dict[int, dict]:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        try:
            data = json.load(f)
            # Skip any non-integer keys safely
            return {int(k): v for k, v in data.items() if k.isdigit()}
        except json.JSONDecodeError:
            return {}


def save_students(data: Dict[int, dict]):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


students_db: Dict[int, dict] = load_students()


@app.post("/students/", status_code=201)
def create_student(student: Student):
    if student.id in students_db:
        raise HTTPException(status_code=400, detail="Student already exists.")
    students_db[student.id] = student.dict()
    save_students(students_db)
    return {"message": "Student created", "student": students_db[student.id]}


@app.get("/students/")
def get_all_students():
    return {"students": list(students_db.values())}

@app.get("/students/{student_id}")
def get_student(student_id: int):
    student = students_db.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    return student


@app.put("/students/{student_id}")
def update_student(student_id: int, updated_student: Student):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found.")
    students_db[student_id] = updated_student.dict()
    save_students(students_db)
    return {"message": "Student updated", "student": students_db[student_id]}


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found.")
    deleted = students_db.pop(student_id)
    save_students(students_db)
    return {"message": "Student deleted", "student": deleted}