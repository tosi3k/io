from django.contrib import admin

# Register your models here.

from .models import Station, Path

admin.site.register(Station)
admin.site.register(Path)
