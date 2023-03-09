from django.urls import path
from .views import MyLoginView, MyLogoutView, RegisterView, MyProfileView, index

app_name = 'account'

urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', MyProfileView.as_view(), name='profile'),
]
