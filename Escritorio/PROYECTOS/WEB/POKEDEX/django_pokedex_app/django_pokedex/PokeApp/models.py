from django.db import models

# Create your models here.

class Pokemon_main(models.Model):
    name = models.CharField(max_length=100)
    unique_id = models.IntegerField(primary_key=True)
    description = models.TextField()
    possible_values = models.CharField(max_length=255) 
    image = models.URLField(blank=True)
    best_stat = models.CharField(max_length=100)
    best_stat_value = models.CharField(max_length=100)

    def __str__(self):
        return self.name
