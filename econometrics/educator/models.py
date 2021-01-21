from django.contrib.auth.models import User
from django.db import models


class Educator(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    name = models.CharField(default="asd", max_length=20)
    family_name = models.CharField(default="asd", max_length=20)
    fathers_name = models.CharField(default="asd", max_length=20)

    def __str__(self):
        return '%s %s %s' % (self.name, self.family_name, self.fathers_name)