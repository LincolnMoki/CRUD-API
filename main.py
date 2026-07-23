# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import init_db, get_connection

init_db()
app = FastAPI()

def row_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
        }


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


@app.get("/tasks", summary="Get all tasks")
def get_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(row) for row in rows]




@app.get("/tasks/{task_id}", summary="Get a single task by ID")
def get_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
            )
    return row_to_dict(row)


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