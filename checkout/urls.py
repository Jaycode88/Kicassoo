from django.urls import path
from . import views
from .views import place_order, order_success, create_payment_intent
from checkout import views as checkout_views

urlpatterns = [
    path('', views.checkout, name='checkout'),  # The main checkout view
    path('place-order/', place_order, name='place_order'),
    path('order-success/', order_success, name='order_success'),
    path(
        'checkout/payment-failed/',
        checkout_views.payment_failed,
        name='payment_failed'),

    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
    path(
        'create-payment-intent/',
        create_payment_intent,
        name='create-payment-intent'),

]
