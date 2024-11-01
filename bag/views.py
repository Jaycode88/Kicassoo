from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product

def view_bag(request):
    """ A view to render the shopping bag contents """
    return render(request, 'bag/bag.html')

def add_to_bag(request, printful_id):
    """Add a quantity of the specified product to the shopping bag"""
    quantity = int(request.POST.get('quantity', 1))
    redirect_url = request.POST.get('redirect_url')

    # Ensure printful_id is always treated as a string in the session
    printful_id = str(printful_id)

    # Retrieve the current bag from session or initialize a new one
    bag = request.session.get('bag', {})
    print(f"Current Bag Before Update: {bag}")

    # Check if product is already in the bag and increment the quantity
    if printful_id in bag:
        bag[printful_id] += quantity
    else:
        bag[printful_id] = quantity

    print(f"Updated Bag: {bag}")

    # Save the updated bag to the session
    request.session['bag'] = bag
    request.session.modified = True  # Ensures session is saved even if nothing else changes

     # Clear delivery-related session data to force recalculation
    request.session.pop('delivery', None)
    request.session.pop('grand_total_with_shipping', None)

    return redirect(redirect_url)



def adjust_bag(request, printful_id):
    """ Adjust the quantity of the specified product to the specified amount """
    product = get_object_or_404(Product, printful_id=printful_id)
    quantity = int(request.POST.get('quantity'))

    bag = request.session.get('bag', {})

    if quantity > 0:
        bag[printful_id] = quantity
    else:
        bag.pop(printful_id)

    request.session['bag'] = bag
    request.session.modified = True

    # Clear delivery-related session data to force recalculation
    request.session.pop('delivery', None)
    request.session.pop('grand_total_with_shipping', None)

    return redirect(reverse('view_bag'))

def remove_from_bag(request, printful_id):
    """ Remove the product from the shopping bag """
    product = get_object_or_404(Product, printful_id=printful_id)

    bag = request.session.get('bag', {})

    # Convert printful_id to string, as session keys might be stored as strings
    printful_id = str(printful_id)

    if printful_id in bag:
        bag.pop(printful_id)  # Remove item from the session bag

    request.session['bag'] = bag  # Update the session
    request.session.modified = True

    # Clear delivery-related session data to force recalculation
    request.session.pop('delivery', None)
    request.session.pop('grand_total_with_shipping', None)

    return redirect('view_bag')  # Redirect back to the bag page after removing


