from django.urls import path
from . import views

urlpatterns = [
    path('my-bottles/', views.UserBottlesView.as_view(), name='user-bottles'),
    path('register/', views.BottleRegisterView.as_view(), name='register-bottle'),
    path('<str:bottle_id>/', views.BottleDetailView.as_view(), name='bottle-detail'),
]
