# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import init_db, get_connection

init_db()
app = FastAPI()

tasks = []

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

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
    tasks = []
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
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title, 0)
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"id": new_id, "title": task.title, "done": False}


@app.put("/tasks/{task_id}", summary="Update an existing task")
def update_task(task_id: int, update: TaskUpdate):
    if not update.title or not update.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    cursor.execute(
        "update tasks set title = ?, done = ? where id = ?",
        (update.title, 1 if update.done else 0, task_id)
    )
    conn.commit()
    conn.close()

    return {"id": task_id, "title": update.title, "done": update.done}

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return