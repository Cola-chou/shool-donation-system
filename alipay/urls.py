from django.contrib import admin
from django.urls import path
from . import views

app_name = 'alipay'

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('index/', views.index),
    path('pay_result/', views.pay_result, name='pay_result'),
    path('<int:item_id>', views.pay, name='pay'),
    # path('^update_order/', views.update_order),
]
