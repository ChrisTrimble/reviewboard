from django_evolution.mutations import AddField
from django.db import models


MUTATIONS = [
    AddField('Repository', 'path', max_length=255)
]
