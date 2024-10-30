from django.shortcuts import render, redirect, reverse
from django.conf import settings
from django.contrib import messages
from .forms import DeliveryForm
import requests
from bag.contexts import bag_contents
import decimal
from decimal import Decimal
import stripe
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from products.printful_service import PrintfulAPI 
import logging
from .models import Order, OrderItem
from .services import prepare_printful_order_data
from django_countries.fields import Country
from products.models import Product
import json


logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    """Main checkout page that calculates delivery and optionally shows payment form."""
    form = DeliveryForm()
    bag_data = bag_contents(request)

    # Check for POST request to calculate delivery
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            # Save order details to session
            request.session['order_details'] = form.cleaned_data

            # Prepare Printful request for shipping rates
            shipping_data = {
                "recipient": {
                    "address1": form.cleaned_data['address_line_1'],
                    "city": form.cleaned_data['city'],
                    "country_code": form.cleaned_data['country'],
                    "zip": form.cleaned_data['postcode'],
                },
                "items": [
                    {"quantity": item['quantity'], "variant_id": item['product'].variant_id}
                    for item in bag_data['bag_items']
                ]
            }

            # Request shipping rates
            try:
                response = requests.post(
                    f"https://api.printful.com/shipping/rates",
                    json=shipping_data,
                    headers={'Authorization': f"Bearer {settings.PRINTFUL_API_KEY}"}
                )
                response_data = response.json()

                if response.status_code == 200:
                    shipping_cost = Decimal(response_data['result'][0]['rate'])
                    request.session['delivery'] = float(shipping_cost)
                else:
                    messages.error(request, f"Could not calculate delivery: {response_data['error']['message']}")
                    shipping_cost = Decimal('0.00')
            except Exception as e:
                messages.error(request, f"Error calculating delivery: {str(e)}")
                shipping_cost = Decimal('0.00')

            # Calculate grand total and save to session
            grand_total_with_shipping = bag_data['grand_total'] + shipping_cost
            request.session['grand_total_with_shipping'] = float(grand_total_with_shipping)

            # Prepare context including all necessary variables
            context = {
                'form': form,
                'bag_items': bag_data['bag_items'],
                'grand_total': bag_data['grand_total'],
                'delivery': shipping_cost,
                'grand_total_with_shipping': grand_total_with_shipping,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY,  # Ensures it is always in the context
            }
            return render(request, 'checkout/checkout.html', context)

    # Default context when the page first loads (no delivery calculated yet)
    context = {
        'form': form,
        'bag_items': bag_data['bag_items'],
        'grand_total': bag_data['grand_total'],
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'checkout/checkout.html', context)


def calculate_delivery(request):
    """Calculate delivery cost using the Printful API and save user details to the session."""
    
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        
        if form.is_valid():
            # Extract form data
            form_data = form.cleaned_data

            # Store the user's details in the session
            request.session['order_details'] = {
                'full_name': form_data['full_name'],
                'email': form_data['email'],
                'phone_number': form_data['phone_number'],
                'address1': form_data['address_line_1'],
                'address2': form_data.get('address_line_2', ''),
                'city': form_data['city'],
                'postcode': form_data['postcode'],
                'country': form_data['country'],
            }
            
            # Prepare data for Printful API call to calculate shipping
            bag_data = bag_contents(request)
            shipping_data = {
                "recipient": {
                    "address1": form_data['address_line_1'],
                    "city": form_data['city'],
                    "country_code": form_data['country'],
                    "zip": form_data['postcode'],
                },
                "items": [
                    {"quantity": item['quantity'], "variant_id": item['product'].variant_id}
                    for item in bag_data['bag_items']
                ]
            }

            try:
                # Request shipping rates from Printful
                response = requests.post(
                    f"https://api.printful.com/shipping/rates",
                    json=shipping_data,
                    headers={'Authorization': f"Bearer {settings.PRINTFUL_API_KEY}"}
                )
                response_data = response.json()

                if response.status_code == 200:
                    shipping_cost = Decimal(response_data['result'][0]['rate'])
                    request.session['delivery'] = float(shipping_cost)  # Save shipping cost to session
                else:
                    messages.error(request, f"Could not calculate delivery: {response_data['error']['message']}")
                    shipping_cost = Decimal('0.00')
            except Exception as e:
                messages.error(request, f"Error calculating delivery: {str(e)}")
                shipping_cost = Decimal('0.00')

            # Calculate grand total with shipping
            grand_total_with_shipping = bag_data['grand_total'] + shipping_cost
            request.session['grand_total_with_shipping'] = float(grand_total_with_shipping)

            # Add items and delivery cost to order details in session
            request.session['order_details']['delivery_cost'] = float(shipping_cost)
            request.session['order_details']['items'] = [
                {'printful_id': item['product'].variant_id, 'quantity': item['quantity']}
                for item in bag_data['bag_items']
            ]

            # Context for rendering the checkout page with updated delivery cost
            context = {
                'form': form,
                'bag_items': bag_data['bag_items'],
                'grand_total': bag_data['grand_total'],
                'delivery': shipping_cost,
                'grand_total_with_shipping': grand_total_with_shipping,
            }

            return render(request, 'checkout/checkout.html', context)

    # Redirect back to checkout if form is invalid or if method is not POST
    return redirect(reverse('checkout'))


def place_order(request):
    """Handles order submission and redirects to payment page with order summary"""

    if request.method == 'POST':
        # Retrieve shipping cost and grand total from session
        try:
            shipping_cost = Decimal(request.session.get('delivery', 0))
            grand_total = Decimal(request.session.get('grand_total', 0))
            grand_total_with_shipping = grand_total + shipping_cost
        except (TypeError, ValueError) as e:
            print(f"Error retrieving or calculating grand total: {e}")
            return HttpResponse("Invalid order total", status=400)

        # Create Stripe PaymentIntent
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(grand_total_with_shipping * 100),  # Convert to cents/pence
                currency='gbp',
                payment_method_types=['card'],
                metadata=request.session.get('checkout_form_data', {})  # Attach metadata if needed
            )
        except Exception as e:
            print(f"Error creating PaymentIntent: {e}")
            return HttpResponse("Failed to create payment intent", status=500)

        # Render payment page with required client_secret and order data
        return render(request, 'checkout/payment_page.html', {
            'client_secret': payment_intent.client_secret,
            'grand_total': grand_total,
            'shipping_cost': shipping_cost,
            'grand_total_with_shipping': grand_total_with_shipping,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        })

    return redirect('checkout')


def order_success(request):
    """Order success page after payment is completed"""
     # Clear the bag after payment success
    request.session['bag'] = {}  # Clear the bag
    request.session.modified = True  # Mark the session as modified to trigger a save
    return render(request, 'checkout/order_success.html')

@csrf_exempt
def create_payment_intent(request):
    if request.method == 'POST':
        try:
            # Parse order details from request body
            order_details = json.loads(request.body)
            print("Order details received in create_payment_intent:", order_details)

            # Validate important fields in `order_details`
            if not order_details.get('full_name') or not order_details.get('items'):
                print("Error: Missing essential fields in order details.")
                return JsonResponse({'error': 'Missing essential fields in order details'}, status=400)

            # Convert items to a JSON string
            items_str = json.dumps(order_details['items'])

            # Create the PaymentIntent with metadata as strings
            payment_intent = stripe.PaymentIntent.create(
                amount=int(order_details['total_amount'] * 100),  # Convert to smallest currency unit
                currency='usd',
                metadata={
                    'full_name': order_details['full_name'],
                    'email': order_details['email'],
                    'phone_number': order_details['phone_number'],
                    'address1': order_details['address1'],
                    'address2': order_details['address2'],
                    'city': order_details['city'],
                    'postcode': order_details['postcode'],
                    'country': order_details['country'],
                    'delivery_cost': str(order_details['delivery_cost']),  # Convert delivery cost to string
                    'items': items_str  # Pass items as JSON string
                },
            )
            return JsonResponse({'clientSecret': payment_intent['client_secret']})

        except Exception as e:
            print(f"Error in create_payment_intent: {e}")
            return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    event = None

    try:
        # Verify the webhook signature
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        print(f"Webhook signature verification failed: {e}")
        return HttpResponse(status=400)

    # Process the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print("💸 Payment intent succeeded:", payment_intent['id'])

        try:
            # Check metadata contents
            metadata = payment_intent.get('metadata', {})
            print("Metadata received in webhook:", metadata)

            # Extract and validate metadata fields with fallbacks
            full_name = metadata.get('full_name', 'No Name Provided')
            email = metadata.get('email', 'no-email@example.com')
            phone_number = metadata.get('phone_number', '0000000000')
            address1 = metadata.get('address1', 'Unknown Address')
            address2 = metadata.get('address2', '')
            city = metadata.get('city', 'Unknown City')
            postcode = metadata.get('postcode', '00000')
            country = metadata.get('country', 'US')
            delivery_cost = Decimal(metadata.get('delivery_cost', '0'))
            items_json = metadata.get('items', '[]')
            
            # Load items; this should ideally be JSON
            try:
                items = json.loads(items_json)
            except json.JSONDecodeError as e:
                print("Failed to decode items JSON:", e)
                items = []  # Default to empty if decoding fails

            # Create Order in Django
            order = Order.objects.create(
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                street_address1=address1,
                street_address2=address2,
                town_or_city=city,
                postcode=postcode,
                country=country,
                delivery_cost=delivery_cost,
                order_total=Decimal(payment_intent['amount_received'] / 100),
                grand_total=Decimal(payment_intent['amount_received'] / 100) + delivery_cost,
                stripe_payment_intent_id=payment_intent['id']
            )
            print(f"Order created with ID: {order.id}")

            # Create each OrderItem for the Order
            for item in items:
                product = Product.objects.get(printful_id=item['printful_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=product.price
                )
            print(f"Order items created for Order ID: {order.id}")

            # Prepare order data for Printful
            printful_api = PrintfulAPI()
            printful_order_data = {
                'recipient': {
                    'name': full_name,
                    'email': email,
                    'phone': phone_number,
                    'address1': address1,
                    'address2': address2,
                    'city': city,
                    'zip': postcode,
                    'country_code': country,
                },
                'items': [
                    {
                        'sync_variant_id': item['printful_id'],  # This is the variant ID in Printful
                        'quantity': item['quantity'],
                    } for item in items
                ]
            }

            # Send order to Printful as a draft
            printful_response = printful_api.create_order(printful_order_data, confirm=False)
            if printful_response:
                order.printful_order_id = printful_response.get('id')
                order.save()
                print("Order successfully sent to Printful.")

        except Exception as e:
            print(f"Error processing order: {e}")
            return HttpResponse(status=500)

    return JsonResponse({'status': 'success'})

def payment_failed(request):
    """Renders the Payment Failed page after a failed payment"""
    return render(request, 'checkout/payment_failed.html')