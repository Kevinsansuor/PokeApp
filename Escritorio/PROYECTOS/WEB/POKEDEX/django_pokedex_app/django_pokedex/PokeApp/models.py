from django.db import models

# Create your models here.

# models.py
from django.db import models

class Usuario(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.name
    

class PageView(models.Model):
    view_count = models.IntegerField(default=0)


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
    
class Pokemon_main_especies(models.Model):
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=255)
    
    class Meta:
        unique_together = ('species', 'name')
    
    def __str__(self):
        return self.name
    
class Pokemon_main_evolutions(models.Model):
    evolutions = models.CharField(max_length=255)
    
    def __str__(self):
        return self.evolutions

class Pokemon_main_abilities(models.Model):
    name = models.CharField(max_length=100)
    abilities = models.CharField(max_length=255)
    
    class Meta:
        unique_together = ('abilities', 'name')
    
    def __str__(self):
        return self.name
