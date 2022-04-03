"""
Celery config file

https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html

"""
from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab

# this code copied from manage.py
# set the default Django settings module for the 'celery' app.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'call_centre_admin_v2.settings')

# you change change the name here
app = Celery("call_centre_admin_v2")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.timezone = 'Asia/Novokuznetsk'

app.conf.beat_schedule = {
    'Назначение задач': {
        'task': 'managers.tasks.task_assign_ticket',
        'schedule': crontab(minute='*/3'),
    },
    'task_reset_hour_counter': {
        'task': 'managers.tasks.task_reset_hour_counter',
        'schedule': crontab(minute=0,
                            hour='0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23'),
    },
    'task_reset_counter': {
        'task': 'managers.tasks.task_reset_counter',
        'schedule': crontab(minute=0, hour=4),
    },
    'task_on_off_online_status': {
        'task': 'managers.tasks.task_on_off_online_status',
        'schedule': crontab(minute='1,16,31,46', hour='0,1,2,3,4,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23'),
    }

}

