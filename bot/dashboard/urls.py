from django.conf.urls import url
from django.contrib import admin
from dashboard import views

urlpatterns = [
    url(r'^TextCloud/', views.GetTextCloud.as_view()),
]
