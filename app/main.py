from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse  # Correct import
from celery.result import AsyncResult

from app.tasks import convert_file_task
from app.celery_app import celery_app

app = FastAPI(title="File Conversion API")

# Ensure required directories exist
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Server Frontend UI
@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = Path("app/templates/index.html")
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend template not found")
    return index_path.read_text()

# 2. Upload and Queue File Endpoint
@app.post("/convert/")
async def convert_file(file: UploadFile = File(...)):
    input_path = UPLOAD_DIR / file.filename
    output_path = OUTPUT_DIR / Path(file.filename).stem

    # Write file asynchronously in chunks to prevent blocking event loop
    with open(input_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            buffer.write(chunk)

    # Convert paths using .as_posix() for Linux/Docker compatibility
    task = convert_file_task.delay(input_path.as_posix(), output_path.as_posix())

    return {
        "task_id": task.id,
        "filename": file.filename,
        "status": "QUEUED"
    }

# Task status endpoint: Frontend calls this endpoint to check the status of a task.
@app.get("/status/{task_id}")
async def get_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task_result.status,   
    }
    if task_result.failed():
        response["error"] = str(task_result.result)

    return response

# File Download Route: Once a task hits SUCCESS, gives client an endpoint to retrieve the finished conversion
@app.get("/download/{filename}")
async def download_file(filename: str):
    # Search for file with matching output_dir
    files = list(OUTPUT_DIR.glob(f"{filename}.*"))

    if not files or not files[0].exists():
        raise HTTPException(status_code=404, detail="Converted File not found")

    return FileResponse(
        path=files[0],
        filename=files[0].name,
        media_type="application/octet-stream"        
    )

def main():
    print("Starting file conversion process...")
    # Optional CLI dispatch test
    print("Task dispatched successfully!")


if __name__ == "__main__":
    main()