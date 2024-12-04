from django.shortcuts import render, redirect, reverse
from django.conf import settings
from django.contrib import messages
from .forms import DeliveryForm
import requests
from bag.contexts import bag_contents
from decimal import Decimal
import stripe
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from products.printful_service import PrintfulAPI
import logging
from .models import Order, OrderItem
from .utils.email import send_order_confirmation_email
from django.db import transaction
import uuid

logger = logging.getLogger('checkout')

stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout(request):
    """view to display checkout form and calculate delivery on user request."""
    bag_data = bag_contents(request)
    form = DeliveryForm(initial=request.session.get('order_details', {}))
    delivery_cost = None
    grand_total_with_shipping = None

    if request.method == 'POST':
        form = DeliveryForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            form_data['address1'] = form_data.pop('address_line_1', None)
            request.session['order_details'] = form_data

            shipping_data = {
                "recipient": {
                    "address1": form_data['address1'],
                    "city": form_data['city'],
                    "country_code": form_data['country'],
                    "zip": form_data['postcode'],
                },
                "items": [
                    {
                        "quantity": item['quantity'],
                        "variant_id": item['product'].variant_id
                    }
                    for item in bag_data['bag_items']
                ]
            }

            headers = {
                'Authorization': f"Bearer {settings.PRINTFUL_API_KEY}"
            }

            try:
                response = requests.post(
                    f"{settings.PRINTFUL_API_URL}/shipping/rates",
                    json=shipping_data,
                    headers=headers
                )
                response_data = response.json()

                if response.status_code == 200:
                    delivery_cost = Decimal(response_data['result'][0]['rate'])
                    grand_total_with_shipping = (
                        bag_data['grand_total'] + delivery_cost
                    )
                    request.session['delivery'] = float(delivery_cost)
                    request.session['grand_total_with_shipping'] = float(
                        grand_total_with_shipping
                    )
                    messages.success(
                        request, "Delivery cost calculated successfully."
                    )
                else:
                    messages.error(
                        request,
                        "Could not calculate delivery:"
                        "Unsupported destination."
                        "Please try again or contact support."
                    )
                    delivery_cost = None
                    grand_total_with_shipping = None
            except Exception as e:
                messages.error(
                    request,
                    (f"Error calculating delivery."
                        "Please try again later or contact support.")
                )
                delivery_cost = None
                grand_total_with_shipping = None

            if delivery_cost is None or grand_total_with_shipping is None:
                return redirect('checkout')

            order = Order.objects.create(
                full_name=form_data['full_name'],
                email=form_data['email'],
                phone_number=form_data['phone_number'],
                street_address1=form_data['address1'],
                street_address2=form_data.get('address2', ''),
                town_or_city=form_data['city'],
                county=form_data.get('county', ''),
                postcode=form_data['postcode'],
                country=form_data['country'],
                delivery_cost=delivery_cost,
                order_total=bag_data['grand_total'],
                grand_total=grand_total_with_shipping,
                payment_status="PENDING",
                order_number=uuid.uuid4().hex.upper()
            )

            for item in bag_data['bag_items']:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price
                )

            payment_intent = stripe.PaymentIntent.create(
                amount=int(order.grand_total * 100),
                currency='usd',
                metadata={'order_number': order.order_number}
            )

            request.session['order_number'] = order.order_number

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
            messages.error(
                request, "Please correct the form errors and try again."
            )

    delivery_value = (
        delivery_cost if delivery_cost is not None
        else request.session.get('delivery')
    )

    context = {
        'form': form,
        'bag_items': bag_data['bag_items'],
        'grand_total': bag_data['grand_total'],
        'delivery': delivery_value,
        'grand_total_with_shipping': (
            grand_total_with_shipping if grand_total_with_shipping is not None
            else request.session.get('grand_total_with_shipping')
        ),
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }

    return render(request, 'checkout/checkout.html', context)


def place_order(request):
    """Handles order submission"""
    if request.method == 'POST':
        try:
            shipping_cost = Decimal(request.session.get('delivery', 0))
            grand_total = Decimal(request.session.get('grand_total', 0))
            grand_total_with_shipping = grand_total + shipping_cost
        except (TypeError, ValueError) as e:
            logger.error(f"Error retrieving or calculating grand total: {e}")
            messages.error(
                request, "An error occurred while calculating the order total."
            )
            return HttpResponse("Invalid order total", status=400)

        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(grand_total_with_shipping * 100),
                currency='gbp',
                payment_method_types=['card'],
                metadata=request.session.get('checkout_form_data', {})
            )
        except Exception as e:
            logger.error(f"Error creating PaymentIntent: {e}")
            messages.error(
                request, "Failed to create payment intent. Please try again."
            )
            return HttpResponse("Failed to create payment intent", status=500)

        return render(request, 'checkout/payment_page.html', {
            'client_secret': payment_intent.client_secret,
            'grand_total': grand_total,
            'shipping_cost': shipping_cost,
            'grand_total_with_shipping': grand_total_with_shipping,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        })

    return redirect('checkout')


def order_success(request):
    """Confirm order success only after verifying payment status."""
    order_number = request.session.get('order_number')
    if not order_number:
        messages.error(request, "Order not found.")
        return redirect('checkout')

    try:
        # Retrieve the order from the database
        order = Order.objects.get(order_number=order_number)
        
        # Verify payment status with Stripe
        if order.stripe_payment_intent_id:
            payment_intent = stripe.PaymentIntent.retrieve(
                order.stripe_payment_intent_id
            )
            if payment_intent['status'] != 'succeeded':
                messages.error(
                    request,
                    "Payment verification failed. Please contact support."
                )
                return redirect('checkout')

        # Mark the order as successful (if not already marked by the webhook)
        if order.payment_status != 'COMPLETED':
            order.payment_status = 'COMPLETED'
            order.save(update_fields=['payment_status'])

        # Clear session data
        request.session.pop('order_number', None)
        request.session.pop('bag', None)
        request.session.modified = True

        return render(request, 'checkout/order_success.html', {'order': order})

    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('checkout')
    except Exception as e:
        logger.error(f"Error confirming order success: {e}")
        messages.error(
            request,
            "An error occurred while confirming your order. Please contact support."
        )
        return redirect('checkout')


@csrf_exempt
def create_payment_intent(request):
    if request.method == 'POST':
        try:
            order_details = request.session.get('order_details', {})
            total_amount = request.session.get(
                'grand_total_with_shipping', None)

            if not order_details.get('address1') or total_amount is None:
                logger.error("Error: Missing required order fields.")
                return JsonResponse(
                    {'error': 'Missing essential fields in order details'},
                    status=400
                )

            amount = int(total_amount * 100) if isinstance(
                total_amount, (int, float, Decimal)
            ) else None
            if amount is None:
                logger.error("Error: Invalid total_amount value.")
                return JsonResponse(
                        {'error': 'Invalid total amount'}, status=400)

            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                metadata={'order_number': request.session.get('order_number')}
            )
            return JsonResponse(
                {'clientSecret': payment_intent['client_secret']})

        except Exception as e:
            logger.error(f"Error in create_payment_intent: {e}")
            return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.error(f"Webhook signature verification failed: {e}")
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_number = payment_intent.get('metadata', {}).get('order_number')
        stripe_intent_id = payment_intent['id']

        logger.info(f"Processing order {order_number} with intent {stripe_intent_id}")

        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(
                    order_number=order_number
                )

                if (
                    order.stripe_payment_intent_id == stripe_intent_id
                    or order.confirmation_email_sent
                ):
                    logger.info(
                        f"Ignoring duplicate or already processed webhook for "
                        f"order {order_number}."
                    )
                    return JsonResponse({'status': 'ignored'}, status=200)

                order.payment_status = 'COMPLETED'
                order.stripe_payment_intent_id = stripe_intent_id
                order.save(update_fields=[
                    'payment_status', 'stripe_payment_intent_id'
                ])

                logger.info(f"Preparing order data for Printful: {order_number}")
                printful_api = PrintfulAPI()
                printful_order_data = {
                    'recipient': {
                        'name': order.full_name,
                        'email': order.email,
                        'phone': order.phone_number,
                        'address1': order.street_address1,
                        'address2': order.street_address2 or '',
                        'city': order.town_or_city,
                        'state_code': order.county,
                        'zip': order.postcode,
                        'country_code': order.country.code,
                    },
                    'items': [
                        {'sync_variant_id': item.product.sync_variant_id,
                         'quantity': item.quantity}
                        for item in order.items.all()
                    ]
                }

                logger.info(f"Sending order to Printful for order {order_number}")
                printful_response = printful_api.create_order(
                    printful_order_data, confirm=False
                )

                logger.info(f"Printful API Response: {printful_response}")

                if printful_response and printful_response.get('result'):
                    result = printful_response['result']

                    # Check if the order is created as a draft
                    if result.get('status') == 'draft':
                        logger.info(f"Order {order_number} created as a draft in Printful.")

                    order.printful_order_id = result.get('id')
                    estimated_shipping_date = result.get('estimated_shipping_date')

                    if estimated_shipping_date:
                        order.estimated_shipping_date = estimated_shipping_date
                    order.save(update_fields=[
                        'printful_order_id', 'estimated_shipping_date'
                    ])

                    for item_data, order_item in zip(
                        result['items'], order.items.all()
                    ):
                        order_item.printful_id = item_data.get('id')
                        order_item.sync_variant_id = item_data.get('sync_variant_id')
                        order_item.printful_variant_id = item_data.get('variant_id')
                        order_item.save()

                    logger.info(f"Printful response for {order_number}: {printful_response}")

                    if not order.confirmation_email_sent:
                        logger.info("Sending order confirmation email.")
                        send_order_confirmation_email(order)
                        order.confirmation_email_sent = True
                        order.save(update_fields=['confirmation_email_sent'])

                else:
                    logger.error(
                        f"Invalid or unexpected Printful response for order {order_number}: {printful_response}"
                    )
                    raise ValueError("Invalid Printful response")

        except Order.DoesNotExist:
            logger.error(f"Order with order number {order_number} not found.")
            return HttpResponse(status=404)
        except Exception as e:
            logger.error(f"Unhandled error processing payment intent: {e}")
            return HttpResponse(status=500)

    elif event['type'] == 'charge.succeeded':
        logger.info(f"Ignoring `charge.succeeded`"
                    "event to prevent duplicate actions.")
        return JsonResponse({'status': 'ignored'}, status=200)

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        order_number = payment_intent.get('metadata', {}).get('order_number')
        logger.warning(
            f"Payment failed for intent {payment_intent['id']} "
            f"for order {order_number}."
        )

        try:
            order = Order.objects.get(order_number=order_number)
            order.payment_status = 'FAILED'
            order.save()
        except Order.DoesNotExist:
            logger.error(
                f"Failed payment for order {order_number} could not be found."
            )

        return JsonResponse({'status': 'payment_failed'}, status=400)

    return JsonResponse({'status': 'success'})



def payment_failed(request):
    """Renders the Payment Failed page after a failed payment"""
    return render(request, 'checkout/payment_failed.html')
