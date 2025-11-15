from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MentionViewSet, AlertViewSet, index, StartFetch, DashboardStats

router = DefaultRouter()
router.register('mentions', MentionViewSet, basename='mention')
router.register('alerts', AlertViewSet, basename='alert')

urlpatterns = [
    path('', index, name='index'),
    path('api/', include(router.urls)),
    path('api/start-fetch/', StartFetch.as_view(), name='start-fetch'),
    path('api/dashboard-stats/', DashboardStats.as_view(), name='dashboard-stats'),
]
