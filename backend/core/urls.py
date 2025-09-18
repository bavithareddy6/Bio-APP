from django.urls import path
from .views import sequences_view, sequences_download_view, expressions_view, expressions_download_view, health

urlpatterns = [
    path('health/', health),
    path('sequences', sequences_view),
    path('sequences/download', sequences_download_view),
    path('expressions', expressions_view),
    path('expressions/download', expressions_download_view),
]

