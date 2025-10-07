from . import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register('plans', views.PlanModelViewSet, basename='plans')


urlpatterns = [
]
urlpatterns += router.urls
