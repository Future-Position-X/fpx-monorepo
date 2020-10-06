from celery import Celery

from app.core.config import settings

celery_app = Celery("worker", broker=settings.CELERY_RABBITMQ_URI)

celery_app.conf.task_routes = {"app.worker.test_celery": "main-queue"}
