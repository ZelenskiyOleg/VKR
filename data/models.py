from django.db import models
from datetime import date
# Create your models here.

class Data(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='First Name')
    last_name = models.CharField(max_length=100, verbose_name='Last Name')
    group = models.CharField(max_length=50, verbose_name='Group')
    username = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name='Username')
    photo = models.ImageField(upload_to='photos/')
    def __str__(self):
        return f'{self.first_name} {self.last_name} | {str(self.group)}'

class Journal(models.Model):
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(Data, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.date} | {self.user.first_name} {str(self.user.last_name)} | {str(self.user.group)}'