import stripe
from django.shortcuts import render, redirect
from .models import OrderItem
from .forms import OrderForm
from products.models import Product
from .services import prepare_printful_order_data
from django.conf import settings
from decimal import Decimal
from products.printful_service import PrintfulAPI
from decimal import Decimal


stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.save()

            # Calculate total and prepare order items
            total_cost = Decimal(0)
            cart_items = []
            for item_id, quantity in request.session.get('bag', {}).items():
                try:
                    product = Product.objects.get(printful_id=item_id)
                    total_cost += product.price * quantity
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price,
                        printful_product_id=product.printful_id,
                    )
                    cart_items.append({
                        'external_variant_id': product.variant_id,
                        'quantity': quantity
                    })
                except Product.DoesNotExist:
                    return redirect('view_bag')

            # Fetch shipping rates based on user's address
            printful_client = PrintfulAPI()
            destination = {
                'country_code': order.country.code,  # Use the user's selected country
                'city': order.town_or_city,
                'address1': order.street_address1,
                'postcode': order.postcode,
            }

            shipping_rates = printful_client.get_shipping_rates(cart_items, destination)
            if shipping_rates:
                shipping_cost = min(rate['rate'] for rate in shipping_rates)
            else:
                shipping_cost = 0  # Default to 0 if no rates are found

            # Add shipping to total cost
            grand_total = total_cost + Decimal(shipping_cost)

            # Create Stripe PaymentIntent
            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(grand_total * 100),  # Amount in pence
                    currency='gbp',
                )
            except stripe.error.StripeError as e:
                print(f"Error creating Stripe PaymentIntent: {e}")
                return redirect('checkout')

            return render(request, 'checkout/checkout.html', {
                'form': form,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
                'client_secret': intent.client_secret,
                'grand_total': grand_total,  # For display in the template
                'shipping_cost': shipping_cost,
            })
    else:
        form = OrderForm()
        return render(request, 'checkout/checkout.html', {
            'form': form,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        })
