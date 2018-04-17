"""ioioio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from rest_api import views as rest_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello', rest_views.api_hello_world),
    # do testów
    path('staty', rest_views.call_staty),
    path('test', rest_views.call_test),
    path('avg', rest_views.call_avg),
    path('dijkstra2/<int:a_id>/<int:b_id>/', rest_views.call_dijkstra),
    path('dijkstra', rest_views.dijkstra)
]
