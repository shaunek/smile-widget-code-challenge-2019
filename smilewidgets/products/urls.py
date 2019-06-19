from django.urls import path
from products import views

urlpatterns = [
    path('products/', views.product_list),
    path('products/<int:id>/', views.product_detail),
    path('get-price/', views.fetch_price),
]