import stripe
from django.shortcuts import render, redirect
from .models import Order, OrderItem
from .forms import OrderForm
from products.models import Product
from .services import PrintfulAPIClient, prepare_printful_order_data
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False) 
            order.save()

            for item_id, quantity in request.session.get('bag', {}).items():
                try:
                    # Log the item_id to see what's being retrieved
                    print(f"Attempting to retrieve product with printful_id: {item_id}")

                    # Fetch product by printful_id
                    product = Product.objects.get(printful_id=item_id)

                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price,
                        printful_product_id=product.printful_id,
                    )
                except Product.DoesNotExist:
                    print(f"Product with printful_id {item_id} not found in the database.")
                    return redirect('view_bag')

            # Send the order to Printful
            printful_client = PrintfulAPIClient(api_key=settings.PRINTFUL_API_KEY)
            printful_order_data = prepare_printful_order_data(order)
            printful_response = printful_client.create_order(printful_order_data, confirm=False)  # Set confirm to True for live orders

            if printful_response and 'id' in printful_response:
                # If the order was successfully created on Printful
                order.printful_order_id = printful_response.get('id')
                order.save()

                # Redirect to order success
                return redirect('order_success', order_number=order.order_number)
            else:
                # If Printful order creation failed, show an error message
                print(f"Printful error: {printful_response}")

            return redirect('order_success', order_number=order.order_number)
        else:
            print('Form is invalid, please check the details.')

    else:
        form = OrderForm()

        # Create Stripe PaymentIntent for the checkout session
        bag = request.session.get('bag', {})
        print(f"Session bag contents: {bag}")
        total_cost = Decimal(0)

        for item_id, quantity in bag.items():
            try:
                product = Product.objects.get(printful_id=item_id)
                total_cost += product.price * quantity
            except Product.DoesNotExist:
                print(f"Product with printful_id {item_id} does not exist.")
                return redirect('view_bag')

        # Convert total to smallest currency unit (pence for GBP)
        total_cost_in_pence = int(total_cost * 100)

        try:
            intent = stripe.PaymentIntent.create(
                amount=total_cost_in_pence,
                currency='gbp',
            )
        except stripe.error.StripeError as e:
            print(f"Error creating Stripe PaymentIntent: {e}")
            return redirect('checkout')

        return render(request, 'checkout/checkout.html', {
            'form': form,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'client_secret': intent.client_secret,
            'grand_total': total_cost,  # For display in the template
        })
