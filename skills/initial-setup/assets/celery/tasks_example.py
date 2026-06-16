from celery import shared_task


@shared_task
def example_task(x: int, y: int) -> int:
    """Example background task."""
    return x + y
