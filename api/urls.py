from django.urls import path

from api.views import CommandView, CommandWithAuthView, HealthCheckView

app_name = 'api'

urlpatterns = [
    path('health-check', HealthCheckView.as_view(), name='health-check'),
    path('command', CommandView.as_view(), name='command'),
    path('command-with-auth', CommandWithAuthView.as_view(), name='auth')
]