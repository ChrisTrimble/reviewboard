from django.db import models

from django_evolution.mutations import AddField


MUTATIONS = [
    AddField('Profile', 'reminder_notification', models.BooleanField,
             initial=True, null=False),
    AddField('Profile', 'reminder_notification_delay', models.IntegerField,
             initial=3, null=True)]
