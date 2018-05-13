from django.contrib import admin
from django.urls import path

from rest_api import views as rest_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dijkstra', rest_views.dijkstra),
    path('stations', rest_views.stations),
    
    # do testów
    path('staty', rest_views.call_staty),
    path('test', rest_views.call_test),
    path('avg', rest_views.call_avg),
    path('dijkstra2/<int:a_id>/<int:b_id>/', rest_views.call_dijkstra)
]
