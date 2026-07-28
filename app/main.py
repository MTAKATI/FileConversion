from fastapi import FastAPI, UploadFile, File
from pathlib import Path
from app.tasks import convert_file_task

app = FastAPI()

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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


def main():
    print("Starting file conversion process...")
    # Optional CLI dispatch test
    print("Task dispatched successfully!")


if __name__ == "__main__":
    main()