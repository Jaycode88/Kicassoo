from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product


def view_bag(request):
    """ A view to render the shopping bag contents """
    return render(request, 'bag/bag.html')


def add_to_bag(request, printful_id):
    """Add a specified product variant and quantity to the shopping bag."""
    quantity = int(request.POST.get('quantity', 1))
    redirect_url = request.POST.get('redirect_url')
    variant_id = request.POST.get('variant_id')

    # Ensure identifiers are treated as strings
    printful_id = str(printful_id)
    variant_id = str(variant_id)

    # Construct the unique item key using product_id and variant_id
    item_key = f"{printful_id}-{variant_id}" if variant_id else printful_id

    # Retrieve the current bag from session or initialize a new one
    bag = request.session.get('bag', {})

    # Update quantity if the item already exists in the bag,
    # or add it with the specified quantity
    if item_key in bag:
        bag[item_key] += quantity
    else:
        bag[item_key] = quantity

    # Save the updated bag back to the session
    request.session['bag'] = bag
    request.session.modified = True

    # Clear delivery-related session data to force recalculation if needed
    request.session.pop('delivery', None)
    request.session.pop('grand_total_with_shipping', None)

    # Fetch product details for the success message
    product = get_object_or_404(
        Product,
        printful_id=printful_id,
        variant_id=variant_id
    )
    item_name = product.name
    item_size = product.size  # Adjust if the product size is stored elsewhere

    # Add a user-friendly success message
    messages.success(
        request,
        f'Added {item_name} (Size: {item_size}) x{quantity} to your bag.',
        extra_tags='add_to_bag alert-success'
    )

    return redirect(redirect_url)


def adjust_bag(request, item_key):
    """Adjust the quantity of the specified product variant."""
    try:
        # Split the item_key to extract product and variant IDs
        product_id, variant_id = item_key.split('-')
    except ValueError:
        messages.error(request, "Invalid item key format.")
        return redirect('view_bag')

    quantity = request.POST.get('quantity', '').strip()

    if not quantity.isdigit():
        messages.error(request, "Please enter a valid quantity.")
        return redirect('view_bag')

    quantity = int(quantity)
    bag = request.session.get('bag', {})

    # Fetch the specific product variant for messaging
    product = get_object_or_404(
        Product,
        printful_id=product_id,
        variant_id=variant_id
    )

    if quantity > 0:
        # Update the quantity in the bag and add a success message
        bag[item_key] = quantity
        messages.success(
            request,
            f'You have updated {product.name} (Size: {product.size}) '
            f'to {quantity} item(s) in your bag.'
        )
    else:
        # Remove the item if quantity is set to zero
        bag.pop(item_key, None)
        messages.success(
            request,
            f"{product.name} (Size: {product.size})"
            "has been removed from your bag."
        )

    # Update the session with the modified bag
    request.session['bag'] = bag
    request.session.modified = True

    # Clear session data related to delivery calculations
    request.session.pop('delivery', None)
    request.session.pop('grand_total_with_shipping', None)

    return redirect('view_bag')


def remove_from_bag(request, item_key):
    """Remove the specified product variant from the shopping bag."""
    bag = request.session.get('bag', {})

    # Extract product and variant IDs from the item key
    try:
        product_id, variant_id = item_key.split('-')
    except ValueError:
        messages.error(request, "An error occurred with the item key format.")
        return redirect('view_bag')

    # Retrieve the specific product variant based on printful_id and variant_id
    product = get_object_or_404(
        Product,
        printful_id=product_id,
        variant_id=variant_id
    )

    if item_key in bag:
        # Remove the item from the bag and add a success message
        del bag[item_key]
        messages.success(
            request,
            f"{product.name} (Size: {product.size}) "
            "has been removed from your bag."
        )
    else:
        messages.warning(request, "Item not found in the bag.")

    # Update the session with the modified bag
    request.session['bag'] = bag
    request.session.modified = True

    # Clear any session data related to delivery calculations
    request.session.pop('delivery', None)
    request.session.pop('grand_total_with_shipping', None)

    return redirect('view_bag')
