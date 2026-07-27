# Runs in the background and executes the conversion tasks without blocking the API (main.py)
# @author: Sandiso Mtakati
# @date: 26/07/2026

from celery import Celery   # Calls the background tasks from Celery library

# Establish connection between Redis and Celery
celery_app = Celery(
    "file_converter", #name of celery app module
    broker="redis://localhost:6379/0",      #redis running locally at the mentioned port and database 0
    backend="redis: //localhost:6379/0"
)

celery_app.conf.update(
    task_serializer="json",     #tells celery to convert function arguments into JSON format before sending them across the network to Redis.
    result_serializer="json",           #celery workers save output data into Redis formatted as JSON
    accepted_content=["json"],              # Celery workers only accepts JSON data.
    result_expires=3600,            # TTL (Time To Live) for task results on Redis. After file conversion the file is saved on Redis, and kept there for 1 hour and deleted from there on to save space.
)