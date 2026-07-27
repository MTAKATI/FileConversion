# For Celery background tasks & Conversion logic inside background workers
# @author: Sandiso Mtakati
# @date: 27/07/2026

from celery import Celery
from app.pipeline.handlers import ValidationHandler, ExecutionHandler, CleanupHandler

app = Celery("file_conversion_worker", broker="redis://localhost:6379/0")

@app.task(name="tasks.convert_file")
def convert_file_task(input_path: str, output_path: str) -> dict:
    # Build execution chain: Validation -> Execution -> Cleanup
    cleanup = CleanupHandler()
    execution = ExecutionHandler(next_handler=cleanup)
    pipeline = ValidationHandler(next_handler=execution)

    # Context object pass through the pipeline
    context = {
        "input_path": input_path,
        "output_path": output_path
    }

    # Run pipeline chain
    result = pipeline.handle(context)

    return {
        "status": result.get("status", "SUCCESS"),
        "result_path": result.get("result_path")
    }