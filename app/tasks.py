from app.celery_app import celery_app
from app.pipeline.handlers import ValidationHandler, ExecutionHandler, CleanupHandler

@celery_app.task(name="app.tasks.convert_file_task")
def convert_file_task(input_path: str, output_path: str) -> dict:
    cleanup = CleanupHandler()
    execution = ExecutionHandler(next_handler=cleanup)
    pipeline = ValidationHandler(next_handler=execution)

    context = {
        "input_path": input_path,
        "output_path": output_path
    }

    result = pipeline.handle(context)

    return {
        "status": result.get("status", "SUCCESS"),
        "result_path": result.get("result_path")
    }