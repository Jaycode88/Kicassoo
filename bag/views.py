from django.shortcuts import render, redirect

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