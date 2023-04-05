from django.urls import path
from .views import NewsDetailView, NewsListView, AnnouncementListView

app_name = 'news'

urlpatterns = [
    path('<int:pk>/', NewsDetailView.as_view(), name='news_detail'),
    path('news_list/', NewsListView.as_view(), name='news_list'),
    path('announcement_list/', AnnouncementListView.as_view(), name='announcement_list')
]
