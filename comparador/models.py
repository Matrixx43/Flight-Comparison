from django.db import models

# Create your models here.
class Aeropuerto(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    codigo = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return f"{self.codigo}"