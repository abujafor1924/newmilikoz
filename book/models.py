from django.db import models

# Create your models here.


class Book(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    publish = models.DateTimeField()

    def __str__(self):
        return self.title
