from celery import Celery
from app.config import settings

celery_app = Celery(
    "worker",
    broker=f"redis://redis:6379/0",
    backend=f"redis://redis:6379/0"
)

celery_app.conf.task_routes = {
    "app.core.tasks.*": "main-queue"
}