# Handles incoming requests from web, authentication and file uploads
# @author: Sandiso Mtakati
# @date: 26/07/2026

# app/tasks.py
from app.celery_app import celery_app
from app.pipeline.handlers import ValidationHandler, ExecutionHandler, CleanupHandler

@celery_app.task(bind=True)
def convert_file_task(self, input_path: str, output_path: str):
    # Construct chain
    cleanup = CleanupHandler()
    execution = ExecutionHandler(next_handler=cleanup)
    pipeline = ValidationHandler(next_handler=execution)

    context = {
        "input_path": input_path,
        "output_path": output_path
    }

    try:
        final_context = pipeline.handle(context)
        return {
            "status": final_context.get("status", "SUCCESS"),
            "result_path": final_context.get("result_path")
        }
    except Exception as exc:
        # Retry task if needed or re-raise exception
        raise self.retry(exc=exc, countdown=5, max_retries=3)