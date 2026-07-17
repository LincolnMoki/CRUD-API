# main.py
from fastapi import FastAPI


app = FastAPI()

@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "Version": "1.0.0",
        "endpoint": ["/tasks"]
    }   
@app.get("/health")
def read_health():
    return {"status": "ok"}