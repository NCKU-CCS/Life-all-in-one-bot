from django.conf.urls import url
from django.contrib import admin
from dashboard import views
# from rest_framework import routers
# from .api import TextCloudViewSet

# getTextCloud = routers.DefaultRouter()
# getTextCloud.register(r'TextCloud', TextCloudViewSet)
urlpatterns = [
	url(r'^$', views.home),
    url(r'^TextCloud/', views.GetTextCloud.as_view()),
    # url(r'^api/', include(getTextCloud.urls)),
]
