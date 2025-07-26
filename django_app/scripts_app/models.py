from django.db import models

# Create your models here.

class Script(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    file_path = models.CharField(max_length=100)  # nombre del .py dentro de 'scripts/'

    def __str__(self):
        return self.name