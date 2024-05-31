from django.urls import path
from . import views
from .views import UsersListAPIView

urlpatterns = [
    path('receive_photo/', views.receive_photo, name='receive_photo'),
    path('journal/', views.journal, name='journal'),
    path('api/users/', UsersListAPIView.as_view(), name='users'),
]