from django.urls import path

from app.views import show_home

urlpatterns = [
    path('', show_home, name="frontend-home"),
]
