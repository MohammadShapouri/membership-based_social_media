from . import views
from django.urls import path
from rest_framework import routers

router = routers.SimpleRouter()
router.register('settings', views.BlockListViewSet, basename='settings')


urlpatterns = [
]
urlpatterns += router.urls
