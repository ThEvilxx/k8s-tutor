from django.urls import path
from . import views
app_name = "practice"
urlpatterns = [
    path("", views.home, name="home"),
    path("questions/<int:pk>/", views.question, name="question"),
    path("attempts/<int:pk>/", views.attempt, name="attempt"),
    path("attempts/<int:pk>/explain/", views.explain, name="explain"),
    path("mistakes/", views.mistakes, name="mistakes"),
]
