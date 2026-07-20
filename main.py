# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

tasks = [
    {"id": 1, "title": "Buy milk", "done": "true "},
    {"id": 2, "title": "Walk the dog", "done": "true"},
    {"id": 3, "title": "Finish assignment", "done": "false"}
]

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

@app.get("/", summary="API Info")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", summary="Health Check")
def health_check():
    return {"status": "ok"}

@app.get("/tasks", summary="Get all tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}", summary="Get a single task by ID")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
        
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400,detail="Task title is required")
    
    new_id = max((t["id"] for t in tasks), default=0) + 1
    new_task = {"id": new_id, "title":task.title,"done":False}
    tasks.append(new_task)
    return new_task

@app.put("/tasks/{task_id}", summary="Update an existing task")
def update_task(task_id: int, update: TaskUpdate):
    if not update.title and update.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    
    for task in tasks:
        if task["id"] == task_id:
            task["title"] == update.title
            task["done"] == update.done
            return task
        
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")