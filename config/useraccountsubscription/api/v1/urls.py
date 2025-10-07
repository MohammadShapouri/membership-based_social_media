from . import views
from django.urls import path
from rest_framework import routers

router = routers.SimpleRouter()
router.register('subscriptions', views.SubscriptionViewSet, basename='subscriptions')


urlpatterns = [
    path('plan-subscribers/<int:pk>', views.PlanSubscriberAPIView.as_view(), name='plan-subscribers'),
]
urlpatterns += router.urls
