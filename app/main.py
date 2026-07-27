# app/main.py
from fastapi import FastAPI, UploadFile, File
from pathlib import Path
import shutil
from app.tasks import convert_file_task

app = FastAPI()

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

@app.post("/convert/")
async def convert_file(file: UploadFile = File(...)):
    input_path = UPLOAD_DIR / file.filename
    output_path = OUTPUT_DIR / Path(file.filename).stem

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Dispatch task to Celery worker asynchronously
    task = convert_file_task.delay(str(input_path), str(output_path))
    
    return {"task_id": task.id, "status": "QUEUED"}

def main():
    print("Starting file conversion process...")
    # Your conversion or task dispatch logic here
    # e.g., result = convert_file.delay("path/to/file")
    print("Task dispatched successfully!")

if __name__ == "__main__":
    main()