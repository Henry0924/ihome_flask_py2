# coding: utf-8

from celery import Celery


app = Celery("ihome")
app.config_from_object("ihome.tasks.config")

# 让celery自己找到任务
app.autodiscover_tasks(["ihome.tasks.sms"])