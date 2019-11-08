from django.db import models

# Create your models here.
class FileContainer (models.Model):
    file = models.FileField()