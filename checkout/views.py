from django.shortcuts import render, redirect, reverse
from django.conf import settings
from django.contrib import messages
from .forms import DeliveryForm
import requests
from bag.contexts import bag_contents
import decimal
import stripe
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from products.printful_service import PrintfulAPI 
import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    """ Checkout page that handles form submission and displays the bag items """
    
    form = DeliveryForm()  # Initialize the form

    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            address_line_1 = form.cleaned_data['address_line_1']
            address_line_2 = form.cleaned_data['address_line_2']
            city = form.cleaned_data['city']
            postcode = form.cleaned_data['postcode']
            country = form.cleaned_data['country']

            print(f"Order Details: {full_name}, {email}, {phone_number}, {address_line_1}, {city}, {postcode}, {country}")

            return redirect(reverse('checkout_success'))

    # Get bag data from context processor
    bag_data = bag_contents(request)

    context = {
        'form': form,  # Pass the form to the template
        'bag_items': bag_data['bag_items'],  # Items in the bag
        'grand_total': bag_data['grand_total'],  # Grand total without shipping (only products)
        'delivery': 0,  # Placeholder for delivery
        'grand_total_with_shipping': bag_data['grand_total'],  # No shipping added yet
    }

    return render(request, 'checkout/checkout.html', context)


def calculate_delivery(request):
    """Calculate delivery cost using the Printful API based on the user's address"""

    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            # Extract form data
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            address_line_1 = form.cleaned_data['address_line_1']
            address_line_2 = form.cleaned_data.get('address_line_2', '')
            city = form.cleaned_data['city']
            postcode = form.cleaned_data['postcode']
            country = form.cleaned_data['country']

            # Prepare request for Printful API
            bag_data = bag_contents(request)
            shipping_data = {
                "recipient": {
                    "address1": address_line_1,
                    "city": city,
                    "country_code": country,
                    "zip": postcode,
                },
                "items": [
                    {"quantity": item['quantity'], "variant_id": item['product'].variant_id}
                    for item in bag_data['bag_items']
                ]
            }

            try:
                # Send request to Printful
                response = requests.post(
                    f"https://api.printful.com/shipping/rates",
                    json=shipping_data,
                    headers={'Authorization': f"Bearer {settings.PRINTFUL_API_KEY}"}
                )
                response_data = response.json()

                if response.status_code == 200:
                    shipping_cost = decimal.Decimal(response_data['result'][0]['rate'])  # Convert shipping cost to Decimal
                    print(f"Shipping Cost: {shipping_cost}")
                    messages.success(request, "Delivery cost calculated!")
                else:
                    shipping_cost = decimal.Decimal('0.00')  # Ensure default is also a Decimal
                    messages.error(request, f"Could not calculate delivery: {response_data['error']['message']}")
            except Exception as e:
                shipping_cost = decimal.Decimal('0.00')  # Ensure default is also a Decimal
                messages.error(request, f"Error calculating delivery: {str(e)}")

            # Add calculated shipping and grand total to context
            grand_total_with_shipping = bag_data['grand_total'] + shipping_cost  # Both are now Decimal
            print(f"Grand Total With Shipping: {grand_total_with_shipping}")
            

            context = {
                'form': form,
                'bag_items': bag_data['bag_items'],
                'grand_total': bag_data['grand_total'],
                'delivery': shipping_cost,  # Make sure this is passed
                'grand_total_with_shipping': grand_total_with_shipping,  # Pass this as well
            }

            messages.success(request, "Test success message!")
            return render(request, 'checkout/checkout.html', context)

        else:
            # Redisplay form if invalid
            return render(request, 'checkout/checkout.html', {'form': form})

    return redirect(reverse('checkout'))


def place_order(request):
    """Handles order submission and redirects to payment page with order summary"""
    
    if request.method == 'POST':
        # Example shipping and grand total data
        shipping_cost = 3.50  # Example value (real one from Printful)
        grand_total = 12.00  # Example total amount (grabbed from session or order)

        # Calculate grand total with shipping
        grand_total_with_shipping = grand_total + shipping_cost

        # Create Stripe PaymentIntent
        payment_intent = stripe.PaymentIntent.create(
            amount=int(grand_total_with_shipping * 100),  # Convert GBP to pence
            currency='gbp',
            payment_method_types=['card'],
        )

        # Pass the values to the template
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
def stripe_webhook(request):
    """Handle Stripe webhooks"""

    # Step 2: Retrieve the webhook payload sent by Stripe
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    # Step 3: Create a Stripe Webhook secret to verify authenticity
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        # Step 4: Verify the payload's signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle successful payments
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Clear the bag when payment is successful
        request.session['bag'] = {}
        print(f"Payment succeeded: {payment_intent['id']}")

    # Handle failed payments
    if event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        error_message = payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')
        print(f"Payment failed: {error_message}")
        # Redirect user to the Payment Failed page
        return redirect('payment_failed')
        

    return JsonResponse({'status': 'success'})

def payment_failed(request):
    """Renders the Payment Failed page after a failed payment"""
    return render(request, 'checkout/payment_failed.html')