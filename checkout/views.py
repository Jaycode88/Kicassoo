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

from django.shortcuts import render, redirect, reverse
from django.conf import settings
from django.contrib import messages
from .forms import DeliveryForm
from bag.contexts import bag_contents
import requests
from decimal import Decimal
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    """Unified view to display checkout form and calculate delivery on user request."""
    bag_data = bag_contents(request)
    form = DeliveryForm(initial=request.session.get('order_details', {}))
    delivery_cost = None
    grand_total_with_shipping = None

    if request.method == 'POST':
        # If the user submits the form, attempt to calculate delivery
        form = DeliveryForm(request.POST)
        
        if form.is_valid():
            form_data = form.cleaned_data

            # Rename `address_line_1` to `address1` for consistency
            form_data['address1'] = form_data.pop('address_line_1', None)

            # Save the modified form data to the session
            request.session['order_details'] = form_data
            print("Order details saved in session:", form_data)  # Debugging

            # Prepare shipping data for Printful
            shipping_data = {
                "recipient": {
                    "address1": form_data['address1'],
                    "city": form_data['city'],
                    "country_code": form_data['country'],
                    "zip": form_data['postcode'],
                },
                "items": [
                    {"quantity": item['quantity'], "variant_id": item['product'].variant_id}
                    for item in bag_data['bag_items']
                ]
            }

            # Calculate delivery cost using the Printful API
            try:
                response = requests.post(
                    f"{settings.PRINTFUL_API_URL}/shipping/rates",
                    json=shipping_data,
                    headers={'Authorization': f"Bearer {settings.PRINTFUL_API_KEY}"}
                )
                response_data = response.json()

                if response.status_code == 200:
                    delivery_cost = Decimal(response_data['result'][0]['rate'])
                    grand_total_with_shipping = bag_data['grand_total'] + delivery_cost
                    request.session['delivery'] = float(delivery_cost)
                    request.session['grand_total_with_shipping'] = float(grand_total_with_shipping)
                    messages.success(request, "Delivery cost calculated successfully.")
                else:
                    messages.error(request, f"Could not calculate delivery: {response_data['error']['message']}")
                    delivery_cost = Decimal('0.00')
            except Exception as e:
                messages.error(request, f"Error calculating delivery: {str(e)}")
                delivery_cost = Decimal('0.00')

        else:
            messages.error(request, "Please correct the form errors and try again.")

    # Context for rendering the checkout page
    context = {
        'form': form,
        'bag_items': bag_data['bag_items'],
        'grand_total': bag_data['grand_total'],
        'delivery': delivery_cost if delivery_cost is not None else request.session.get('delivery'),  
        'grand_total_with_shipping': grand_total_with_shipping if grand_total_with_shipping is not None else request.session.get('grand_total_with_shipping'),
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'order_details': request.session.get('order_details', {})
    }

    return render(request, 'checkout/checkout.html', context)


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
            order_details = json.loads(request.body)
            print("Order details retrieved in create_payment_intent:", order_details)

            if not order_details.get('address1'):
                print("Error: Missing `address1` in order details.")
                return JsonResponse({'error': 'Missing essential fields in order details'}, status=400)

            items_metadata = [
                {
                    'sync_variant_id': item['sync_variant_id'],
                    'printful_id': item.get('printful_id', ''),
                    'variant_id': item.get('variant_id', ''),
                    'quantity': item['quantity']
                }
                for item in order_details['items']
            ]

            payment_intent = stripe.PaymentIntent.create(
                amount=int(order_details['total_amount'] * 100),
                currency='usd',
                metadata={
                    'full_name': order_details['full_name'],
                    'email': order_details['email'],
                    'phone_number': order_details['phone_number'],
                    'address1': order_details['address1'],
                    'address2': order_details.get('address2', ''),
                    'city': order_details['city'],
                    'postcode': order_details['postcode'],
                    'country': order_details['country'],
                    'delivery_cost': order_details['delivery_cost'],
                    'items': json.dumps(items_metadata)
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
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        print(f"Webhook signature verification failed: {e}")
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print("💸 Payment intent succeeded:", payment_intent['id'])

        try:
            # Retrieve metadata
            metadata = payment_intent.get('metadata', {})
            items = json.loads(metadata.get('items', '[]'))
            address1 = metadata.get('address1')

            # Verify address1 presence
            if not address1:
                print("Error: Address line 1 is missing in webhook metadata.")
                return HttpResponse("Missing address line 1", status=400)

            # Create Order in Django
            order = Order.objects.create(
                full_name=metadata.get('full_name', 'No Name Provided'),
                email=metadata.get('email', 'no-email@example.com'),
                phone_number=metadata.get('phone_number', '0000000000'),
                street_address1=address1,
                street_address2=metadata.get('address2', ''),
                town_or_city=metadata.get('city', 'Unknown City'),
                postcode=metadata.get('postcode', '00000'),
                country=metadata.get('country', 'US'),
                delivery_cost=Decimal(metadata.get('delivery_cost', '0')),
                order_total=Decimal(payment_intent['amount_received'] / 100),
                grand_total=Decimal(payment_intent['amount_received'] / 100) + Decimal(metadata.get('delivery_cost', '0')),
                stripe_payment_intent_id=payment_intent['id']
            )
            print(f"Order created with ID: {order.id}")

            # Create each OrderItem for the Order, using multiple ID checks
            for item in items:
                product = None
                # Attempt to find product by sync_variant_id, printful_id, or variant_id
                for id_field in ['sync_variant_id', 'printful_id', 'variant_id']:
                    try:
                        product = Product.objects.get(**{id_field: item[id_field]})
                        break  # Exit loop if product is found
                    except Product.DoesNotExist:
                        continue

                if not product:
                    print(f"Error: Product with any of the provided IDs (sync_variant_id, printful_id, variant_id) not found in DB for item: {item}")
                    return HttpResponse("Product not found", status=404)

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
                    'name': metadata.get('full_name', 'No Name Provided'),
                    'email': metadata.get('email', 'no-email@example.com'),
                    'phone': metadata.get('phone_number', '0000000000'),
                    'address1': address1,
                    'address2': metadata.get('address2', ''),
                    'city': metadata.get('city', 'Unknown City'),
                    'zip': metadata.get('postcode', '00000'),
                    'country_code': metadata.get('country', 'US'),
                },
                'items': [
                    {
                        'sync_variant_id': item['sync_variant_id'],
                        'quantity': item['quantity']
                    } for item in items
                ]
            }

            # Send the order to Printful
            printful_response = printful_api.create_order(printful_order_data, confirm=False)
            if printful_response:
                order.printful_order_id = printful_response.get('id')
                order.save()
                print("Order successfully sent to Printful.")

        except Exception as e:
            print(f"Error processing order in Printful: {e}")
            return HttpResponse(status=500)

    return JsonResponse({'status': 'success'})


def payment_failed(request):
    """Renders the Payment Failed page after a failed payment"""
    return render(request, 'checkout/payment_failed.html')