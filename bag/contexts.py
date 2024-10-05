from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

def bag_contents(request):
    """
    Get all items in the bag to be available site-wide.
    """
    bag = request.session.get('bag', {})
    bag_items = []
    total = 0
    product_count = 0

    for printful_id, quantity in bag.items():
        product = get_object_or_404(Product, printful_id=printful_id)
        subtotal = quantity * product.price  # Calculate subtotal here
        total += subtotal  # Add subtotal to total
        product_count += quantity
        bag_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,  # Include subtotal in bag items
        })

    grand_total = total

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'grand_total': grand_total,
    }

    return context
