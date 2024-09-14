from django.shortcuts import render, redirect
from .models import Order, OrderItem
from django.contrib import messages
from .forms import OrderForm
from products.models import Product
from .services import PrintfulAPIClient, prepare_printful_order_data
from django.conf import settings

def checkout(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)  # Create the order but don't save it yet
            order.save()  # Now save the order to the database

            # Create OrderItems for each item in the bag
            for item in request.session.get('bag', []):
                product = Product.objects.get(variant_id=item['varient_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=product.price,
                    printful_product_id=product.variant_id,  
                )

            # Send the order to Printful
            printful_client = PrintfulAPIClient(api_key=settings.PRINTFUL_API_KEY)
            printful_order_data = prepare_printful_order_data(order)  # Prepare data for Printful
            printful_response = printful_client.create_order(printful_order_data, confirm=False)  # Set confirm to True for live orders

            if printful_response and 'id' in printful_response:
                # If the order was successfully created on Printful
                order.printful_order_id = printful_response.get('id')
                order.save()  # Save the Printful order ID to the order

                # Redirect to a success page
                return redirect('order_success', order_number=order.order_number)
            else:
                # If Printful order creation failed, show an error message
                messages.error(request, 'There was an error processing your order with Printful. Please try again.')
                # Optionally, log the error response from Printful for debugging
                print(f"Printful error: {printful_response}")

        else:
            messages.error(request, 'There was an error with your form. Please check the details.')

    else:
        form = OrderForm()

    return render(request, 'checkout/checkout.html', {'form': form})
