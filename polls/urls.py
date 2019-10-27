from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('vehicles/', views.vehicles, name='vehicles'),
    path('incomes/', views.incomes, name='incomes'),
    path('properties/', views.properties, name='properties'),
    path('land/', views.land_owned, name='land')
]