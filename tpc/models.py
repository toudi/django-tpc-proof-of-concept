from django.db import models


# Create your models here.
class MyModel(models.Model):
    foo = models.CharField(max_length=23)
