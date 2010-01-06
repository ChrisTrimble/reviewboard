from django.db import models

from django_evolution.mutations import AddField

MUTATIONS = [
    AddField('Comment', 'blocks_submission', models.BooleanField,
             initial=False, null=False)]
