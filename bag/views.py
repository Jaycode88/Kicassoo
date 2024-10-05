from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product

def view_bag(request):
    """ A view to render the shopping bag contents """
    return render(request, 'bag/bag.html')

def add_to_bag(request, printful_id):
    """ Add a quantity of a specific product to the shopping bag """
    product = get_object_or_404(Product, printful_id=printful_id)
    quantity = int(request.POST.get('quantity'))

    bag = request.session.get('bag', {})

    if printful_id in bag:
        bag[printful_id] += quantity
    else:
        bag[printful_id] = quantity

    request.session['bag'] = bag
    messages.success(request, f'Added {product.name} to your bag')
    return redirect(reverse('product_list'))

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
    return redirect('view_bag')  # Redirect back to the bag page after removing


