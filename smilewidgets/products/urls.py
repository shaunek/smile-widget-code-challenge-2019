from django.urls import path
from products import views

urlpatterns = [
    path('get-price/', views.fetch_price),
]