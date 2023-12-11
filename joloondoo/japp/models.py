from django.db import models


class Subject(models.Model):
    s_images = models.ImageField(upload_to='subjects/', blank=True, null=True)
class Question(models.Model):
    q_images = models.ImageField(upload_to='questions/', blank=True, null=True)
