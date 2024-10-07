from django.urls import path
from . import views
from .views import place_order, order_success

urlpatterns = [
    path('', views.checkout, name='checkout'),  # The main checkout view
    path('calculate-delivery/', views.calculate_delivery, name='calculate_delivery'),  # The view to calculate delivery
    path('place-order/', place_order, name='place_order'),
    path('order-success/', order_success, name='order_success'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
]
