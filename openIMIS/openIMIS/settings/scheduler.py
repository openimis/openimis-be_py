import os
# This scheduler config will:
# - Store jobs in the project database
# - Execute jobs in threads inside the application process, for production use, we could use a dedicated process
SCHEDULER_CONFIG = {
    "apscheduler.jobstores.default": {
        "class": "django_apscheduler.jobstores:DjangoJobStore"
    },
    "apscheduler.executors.processpool": {"type": "threadpool"},
}

SCHEDULER_AUTOSTART = os.environ.get("SCHEDULER_AUTOSTART", False)

# Normally, one creates a "scheduler" method that calls the appropriate scheduler.add_job but since we are in a
# modular architecture and calling only once from the core module, this has to be dynamic.
# This list will be called with scheduler.add_job() as specified:
# Note that the document implies that the time is local and follows DST but that seems false and in UTC regardless
SCHEDULER_JOBS = [
    # {
    #     "method": "policy_notification.tasks.send_notification_messages",
    #     "args": ["cron"],
    #     "kwargs": {"id": "openimis_notification_batch", 'day_of_week': '*',
    #                "hour": "8,12,16,20", "replace_existing": True},
    # },
    # {
    #     "method": "claim_ai_quality.tasks.claim_ai_processing",
    #     "args": ["cron"],
    #     "kwargs": {"id": "claim_ai_processing",
    #                "hour": 0
    #                "minute", 30
    #                "replace_existing": True},
    # },
]
# This one is called directly with the scheduler object as first parameter. The methods can schedule things on their own
SCHEDULER_CUSTOM = [
    {
        "method": "core.tasks.sample_method",
        "args": ["sample"],
        "kwargs": {"sample_named": "param"},
    },
]
