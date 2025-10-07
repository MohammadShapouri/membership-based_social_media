from . import views
from django.urls import path
from rest_framework import routers

router = routers.SimpleRouter()
router.register('follower-followings', views.FollowerFollowingViewSet, basename='follower-followings')
router.register('blocklists', views.BlockListViewSet, basename='blocklists')


urlpatterns = [
    path('follow-stats/<int:pk>', views.UserFollowStatsAPIView.as_view(), name='follow-stats'),
    path('current-user-following-stats/<int:pk>', views.CurrentUserFollowingStatsAPIView.as_view(), name='current-user-following-stats'),
    path('current-user-block-stats/<int:pk>', views.CurrentUserBlockStatsAPIView.as_view(), name='current-user-block-stats'),
]
urlpatterns += router.urls
