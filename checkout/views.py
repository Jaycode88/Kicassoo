from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from bag.contexts import bag_contents

def checkout(request):
    """ Checkout page that handles form submission and displays the bag items """

    # Handle form submission (POST request)
    if request.method == 'POST':
        # Retrieve the data from the form
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        country = request.POST.get('country')

        # For now, you can just print these details to the console to check they're being collected
        print(f"Order Details: {full_name}, {email}, {phone_number}, {address_line_1}, {city}, {postcode}, {country}")
        
        # Redirect to a success page (to be built later)
        return redirect(reverse('checkout_success'))  # We'll create this page next

    # Handle GET request (display form and order details)
    bag_data = bag_contents(request)  # Get the bag details from the context processor

    context = {
        'bag_items': bag_data['bag_items'],
        'grand_total': bag_data['grand_total'],
        'delivery': 0,  # This will be calculated later
        'grand_total_with_shipping': bag_data['grand_total'],  # Will include delivery later
    }

    return render(request, 'checkout/checkout.html', context)
