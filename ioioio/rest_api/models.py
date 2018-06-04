from django.db import models
from datetime import datetime


class Station(models.Model):
    name      = models.CharField(max_length=64)
    latitude  = models.CharField(max_length=16)
    longitude = models.CharField(max_length=16)


class Path(models.Model):
    time      = models.IntegerField()
    length    = models.IntegerField(default = -1)
    station_a = models.ForeignKey(Station, related_name='station_a', on_delete=models.CASCADE)
    station_b = models.ForeignKey(Station, related_name='station_b', on_delete=models.CASCADE)
    last_update = models.DateTimeField(auto_now = True)


class Email(models.Model):
    topic       = models.TextField(max_length=64)
    first_name  = models.CharField(max_length=32)
    second_name = models.CharField(max_length=32)
    email       = models.TextField(max_length=64)
    content     = models.TextField()

    def __str__(self):
        return '{} ({} {})'.format(self.topic, self.first_name, self.second_name)
