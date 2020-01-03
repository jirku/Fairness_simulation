from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('setting/', views.setting, name='setting'),
    path('model/', views.model, name='model'),
]
