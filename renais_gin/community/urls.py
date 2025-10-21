# community/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('circles/', views.CommunityCircleListCreateView.as_view(), name='circle-list'),
    path('circles/<int:pk>/', views.CommunityCircleDetailView.as_view(), name='circle-detail'),
    path('stories/', views.CommunityStoryListCreateView.as_view(), name='story-list'),
    path('stories/<int:pk>/', views.CommunityStoryDetailView.as_view(), name='story-detail'),
]