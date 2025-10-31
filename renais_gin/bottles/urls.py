from django.urls import path
from . import views

urlpatterns = [
    # Web views
    path('my-bottles/', views.UserBottlesView.as_view(), name='user-bottles'),
    path('register/', views.BottleRegisterView.as_view(), name='register-bottle'),
    path('<str:bottle_id>/', views.BottleDetailView.as_view(), name='bottle-detail'),

    # API endpoints for bottles.html frontend
    path('api/register/', views.register_bottle_api, name='api-register-bottle'),
    path('api/my-bottles/', views.my_bottles_api, name='api-my-bottles'),
]
