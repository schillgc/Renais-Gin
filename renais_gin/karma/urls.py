from django.urls import path
from . import views

urlpatterns = [
    path('pledges/', views.KarmaPledgeListCreateView.as_view(), name='pledge-list'),
    path('pledges/<str:submission_id>/', views.KarmaPledgeDetailView.as_view(), name='pledge-detail'),
    path('validations/', views.PledgeValidationListView.as_view(), name='validation-list'),
    path('validate/', views.KarmaValidationCreateView.as_view(), name='validation-create'),
    path('rebates/', views.RebateListView.as_view(), name='rebate-list'),
    path('dashboard/', views.karma_dashboard, name='karma-dashboard'),
]
