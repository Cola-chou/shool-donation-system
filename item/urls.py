from django.urls import path
from . import views

app_name = 'item'

urlpatterns = [
    path('<int:record_id>/', views.record_items, name='record_items_list'),
    path('create/<int:project_id>/<int:request_id>/',
         views.donation_item_create,
         name='donation_item_create'),
    path('change/<int:record_id>/<int:item_id>/',
         views.donation_item_change,
         name='donation_item_change'),
    path('delete/<int:record_id>/<int:item_id>/',
         views.donation_item_delete, name='donation_item_delete'),
]
