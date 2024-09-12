from django.shortcuts import render, redirect
from django.http import JsonResponse

def view_bag(request):
    """ A view that renders the bag contents page """
    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """
    
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    bag = request.session.get('bag', {})

    # If the item is already in the bag, increase the quantity
    if item_id in bag:
        bag[item_id] += quantity  # Increment the existing quantity
    else:
        bag[item_id] = quantity  # Add a new item with the specified quantity

    # Update the session
    request.session['bag'] = bag
    print(request.session['bag'])  # For debugging purposes, this can be removed later
    return redirect(redirect_url)


def update_bag(request):
    """Update the quantity of a product in the shopping bag."""
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1  # Prevent negative or zero quantities
        except ValueError:
            quantity = 1  # Default to 1 if invalid input is provided
        
        bag = request.session.get('bag', {})

        if 'increment' in request.POST:
            bag[item_id] = bag.get(item_id, 0) + 1
        elif 'decrement' in request.POST and bag.get(item_id, 0) > 1:
            bag[item_id] = bag.get(item_id) - 1
        else:
            bag[item_id] = quantity

        request.session['bag'] = bag
        return redirect('view_bag')
    return JsonResponse({'status': 'fail'}, status=400)


def remove_from_bag(request, item_id):
    """Remove a product from the shopping bag."""
    if request.method == 'POST':
        bag = request.session.get('bag', {})

        if item_id in bag:
            del bag[item_id]

        request.session['bag'] = bag
        return redirect('view_bag')
    return JsonResponse({'status': 'fail'}, status=400)