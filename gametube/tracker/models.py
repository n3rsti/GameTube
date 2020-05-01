from django.db import models

# Create your models here.
class LolVersion(models.Model):
    patch = models.CharField(max_length=30)

class Champion(models.Model):
    name = models.CharField(max_length=300)
    champion_id = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return f'{self.name}: {self.champion_id}'