# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import init_db

init_db()
app = FastAPI()

DEFAULT_TASKS = [
    {"id": 1, "title": "Buy milk", "done": True},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Finish assignment", "done": False}
]

tasks = [t.copy() for t in DEFAULT_TASKS]
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

@app.get("/stats", summary="Get task statistics")
def get_stats():
    total = len(tasks)
    done_count = sum(1 for t in tasks if t['done'])
    return{
        "total_tasks": total,
        "done": done_count,
        "open": total - done_count
    }

@app.post("/reset", summary="reset tasks back to three examples")
def reset_tasks():
    global tasks
    tasks = [t.copy() for t in DEFAULT_TASKS]
    return {"message": "Tasks reset to default examples"}


@app.get("/tasks", summary="list search with optional filtering and search")
def get_tasks(done: Optional[bool]= None, search: Optional[str]=None):
    result = tasks

    if done is not None:
        result = [t for t in result if t["done"]==done]
    
    if search is not None:
        result = [t for t in result if search.lower() in t["title"].lower()]

    return result




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
    if not update.title or not update.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = update.title
            task["done"] = update.done
            return task
        
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")