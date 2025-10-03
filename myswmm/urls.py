from django.urls import path
from .views import RunSWMMAPIView

urlpatterns = [
    path("run-simulation/", RunSWMMAPIView.as_view(), name="run-simulation"),
]
