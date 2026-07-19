   # weather/urls.py
from django.urls import path
from . import views

urlpatterns = [
       path('', views.index, name='index'),
   ]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('tornadoes/', views.tornado_list, name='tornado_list'),
]