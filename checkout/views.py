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
import uuid


logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout(request):
    """Unified view to display checkout form and calculate delivery on user request."""
    bag_data = bag_contents(request)
    form = DeliveryForm(initial=request.session.get('order_details', {}))
    delivery_cost = None
    grand_total_with_shipping = None

    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        
        if form.is_valid():
            form_data = form.cleaned_data
            form_data['address1'] = form_data.pop('address_line_1', None)
            request.session['order_details'] = form_data  # Save details to session

            # Prepare shipping data and calculate cost using Printful API
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

            # Create draft order in Django
            order = Order.objects.create(
                full_name=form_data['full_name'],
                email=form_data['email'],
                phone_number=form_data['phone_number'],
                street_address1=form_data['address1'],
                street_address2=form_data.get('address2', ''),
                town_or_city=form_data['city'],
                postcode=form_data['postcode'],
                country=form_data['country'],
                delivery_cost=delivery_cost,
                order_total=bag_data['grand_total'],
                grand_total=grand_total_with_shipping,
                order_number=uuid.uuid4().hex.upper()
            )

            # Save order items
            for item in bag_data['bag_items']:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price
                )

            # Create Stripe PaymentIntent with essential metadata
            payment_intent = stripe.PaymentIntent.create(
                amount=int(order.grand_total * 100),
                currency='usd',
                metadata={'order_number': order.order_number}  # Pass the order number only
            )

            # Save the order number in the session for webhook reference
            request.session['order_number'] = order.order_number

            # Render the checkout page with payment intent client_secret
            return render(request, 'checkout/checkout.html', {
                'form': form,
                'bag_items': bag_data['bag_items'],
                'grand_total': bag_data['grand_total'],
                'delivery': delivery_cost,
                'grand_total_with_shipping': grand_total_with_shipping,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
                'client_secret': payment_intent.client_secret
            })
        else:
            messages.error(request, "Please correct the form errors and try again.")

    context = {
        'form': form,
        'bag_items': bag_data['bag_items'],
        'grand_total': bag_data['grand_total'],
        'delivery': delivery_cost if delivery_cost is not None else request.session.get('delivery'),  
        'grand_total_with_shipping': grand_total_with_shipping if grand_total_with_shipping is not None else request.session.get('grand_total_with_shipping'),
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
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
            # Retrieve order details from session
            order_details = request.session.get('order_details', {})
            total_amount = request.session.get('grand_total_with_shipping', None)

            # Check if essential fields are present
            if not order_details.get('address1') or total_amount is None:
                print("Error: Missing required order fields.")
                return JsonResponse({'error': 'Missing essential fields in order details'}, status=400)

            # Convert total_amount to an integer in cents for Stripe (if it is not already)
            amount = int(total_amount * 100) if isinstance(total_amount, (int, float, Decimal)) else None
            if amount is None:
                print("Error: Invalid total_amount value.")
                return JsonResponse({'error': 'Invalid total amount'}, status=400)

            # Metadata now only includes the order number
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                metadata={'order_number': request.session.get('order_number')}
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
        # Verify and construct event from Stripe
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.error(f"Webhook signature verification failed: {e}")
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        logger.info(f"💸 Payment intent succeeded: {payment_intent['id']}")

        try:
            # Retrieve order using the order number in metadata
            order_number = payment_intent.get('metadata', {}).get('order_number')
            order = Order.objects.get(order_number=order_number)
            
            # Save the Stripe Payment Intent ID to the Order
            order.stripe_payment_intent_id = payment_intent['id']
            order.save()

            # Prepare Printful order data using sync_variant_id
            printful_api = PrintfulAPI()
            printful_order_data = {
                'recipient': {
                    'name': order.full_name,
                    'email': order.email,
                    'phone': order.phone_number,
                    'address1': order.street_address1,
                    'address2': order.street_address2 or '',
                    'city': order.town_or_city,
                    'zip': order.postcode,
                    'country_code': order.country.code,
                },
                'items': [
                    {
                        'sync_variant_id': item.product.sync_variant_id,  # Use sync_variant_id here
                        'quantity': item.quantity
                    } for item in order.items.all()
                ]
            }

            # Send the order to Printful and retrieve the response
            printful_response = printful_api.create_order(printful_order_data, confirm=True)
            logger.info(f"Printful API Response: {printful_response}")

            # Check if 'result' and 'items' are present in the response
            if printful_response and 'result' in printful_response and 'items' in printful_response['result']:
                order.printful_order_id = printful_response['result'].get('id')
                order.save()

                # Update each OrderItem with Printful IDs
                for item_data, order_item in zip(printful_response['result']['items'], order.items.all()):
                    # Map fields: printful_id should be Printful's item 'id', sync_variant_id stays as the identifier
                    order_item.printful_id = item_data.get('id')
                    order_item.sync_variant_id = item_data.get('sync_variant_id')  # Make sure sync_variant_id is saved
                    order_item.printful_variant_id = item_data.get('variant_id')  # Printful’s variant ID
                    order_item.save()

                logger.info("Order and items successfully sent to Printful with updated IDs.")
            else:
                logger.warning("Warning: 'items' key missing in Printful response or response is empty.")
                return HttpResponse("Error: 'items' key missing in Printful response.", status=500)

        except Order.DoesNotExist:
            logger.error(f"Order with order number {order_number} not found.")
            return HttpResponse(status=404)
        except Exception as e:
            logger.error(f"Error processing order in Printful: {e}")
            return HttpResponse(status=500)

    return JsonResponse({'status': 'success'})



def payment_failed(request):
    """Renders the Payment Failed page after a failed payment"""
    return render(request, 'checkout/payment_failed.html')