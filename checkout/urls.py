from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),  # The main checkout view
    path('calculate-delivery/', views.calculate_delivery, name='calculate_delivery'),  # The view to calculate delivery
    ]
