from django.urls import path
from .views import DonationProjectListView, DonationProjectDetailView

app_name = 'donation'

urlpatterns = [
    path('', DonationProjectListView.as_view(), name='project_list'),
    path('<int:pk>/', DonationProjectDetailView.as_view(), name='project_detail'),
]
