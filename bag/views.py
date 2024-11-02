from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product

def view_bag(request):
    """ A view to render the shopping bag contents """
    return render(request, 'bag/bag.html')

def add_to_bag(request, printful_id):
    """Add a specified product variant and quantity to the shopping bag."""
    quantity = int(request.POST.get('quantity', 1))
    redirect_url = request.POST.get('redirect_url')
    variant_id = request.POST.get('variant_id')  # Retrieve variant_id from form submission

    # Ensure identifiers are treated as strings
    printful_id = str(printful_id)
    variant_id = str(variant_id)
    
    # Construct a unique item key for each product variant
    item_key = f"{printful_id}-{variant_id}"

    # Retrieve the current bag from session or initialize a new one
    bag = request.session.get('bag', {})
    print(f"Current Bag Before Update: {bag}")

    # Check if the specific variant is already in the bag; if so, update the quantity
    if item_key in bag:
        bag[item_key] += quantity
    else:
        bag[item_key] = quantity

    print(f"Updated Bag: {bag}")

    # Save the updated bag to the session
    request.session['bag'] = bag
    request.session.modified = True  # Ensures session is saved even if nothing else changes

    # Clear delivery-related session data to force recalculation if needed
    request.session.pop('delivery', None)
    request.session.pop('grand_total_with_shipping', None)

    return redirect(redirect_url)


def adjust_bag(request, item_key):
    """Adjust the quantity of the specified product variant."""
    try:
        product_id, variant_id = item_key.split('-')
    except ValueError:
        messages.error(request, "Invalid item key.")
        return redirect('view_bag')
    
    quantity = request.POST.get('quantity', '').strip()
    
    if not quantity.isdigit():
        messages.error(request, "Please enter a valid quantity.")
        return redirect('view_bag')

    quantity = int(quantity)
    bag = request.session.get('bag', {})

    if quantity > 0:
        bag[item_key] = quantity
    else:
        bag.pop(item_key, None)

    request.session['bag'] = bag
    request.session.modified = True
    request.session.pop('delivery', None)
    request.session.pop('grand_total_with_shipping', None)

    return redirect('view_bag')


def remove_from_bag(request, item_key):
    """Remove the specified product variant from the shopping bag."""
    bag = request.session.get('bag', {})

    if item_key in bag:
        del bag[item_key]

    request.session['bag'] = bag
    request.session.modified = True
    request.session.pop('delivery', None)
    request.session.pop('grand_total_with_shipping', None)

    return redirect('view_bag')
