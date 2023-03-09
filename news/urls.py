from django.urls import path
from .views import NewDetailView

app_name = 'news'

urlpatterns = [
    path('<int:pk>/', NewDetailView.as_view(), name='new_detail')
]
