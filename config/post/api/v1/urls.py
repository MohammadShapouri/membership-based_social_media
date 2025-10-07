from . import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register('posts', views.PostViewSet, basename='posts')


urlpatterns = [
]
urlpatterns += router.urls
