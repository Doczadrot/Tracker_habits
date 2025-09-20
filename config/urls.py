from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from .health_views import health_check, detailed_health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("habits.urls", namespace="habits")),
    path("users/", include("users.urls", namespace="users")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularRedocView.as_view(url_name="schema"), name="docs"),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Health check endpoints
    path("health/", health_check, name="health_check"),
    path("health/detailed/", detailed_health_check, name="detailed_health_check"),
]
