from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MentionViewSet, AlertViewSet, index, StartFetch, DashboardStats,
    dashboard_view, mentions_view, alerts_view, feeds_view
)

router = DefaultRouter()
router.register('mentions', MentionViewSet, basename='mention')
router.register('alerts', AlertViewSet, basename='alert')

urlpatterns = [
    path('', index, name='index'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('mentions/', mentions_view, name='mentions'),
    path('alerts/', alerts_view, name='alerts'),
    path('feeds/', feeds_view, name='feeds'),
    # API endpoints (kept for backward compatibility or future use)
    path('api/', include(router.urls)),
    path('api/start-fetch/', StartFetch.as_view(), name='start-fetch'),
    path('api/dashboard-stats/', DashboardStats.as_view(), name='dashboard-stats'),
]
