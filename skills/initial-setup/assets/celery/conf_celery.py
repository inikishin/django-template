from app.config.environ import env

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/2")

CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

# In tests, tasks run synchronously (eager), without a broker.
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_ALWAYS_EAGER", default=False)
CELERY_TASK_EAGER_PROPAGATES = True

# The schedule of periodic tasks is stored in the DB (django-celery-beat).
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
