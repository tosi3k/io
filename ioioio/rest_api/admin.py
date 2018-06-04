from django.contrib import admin

# Register your models here.

from .models import Station, Path, Email

admin.site.register(Station)
admin.site.register(Path)
admin.site.register(Email)
