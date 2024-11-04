from decimal import Decimal
from django.shortcuts import get_object_or_404
from products.models import Product

def bag_contents(request):
    """Calculate and return bag contents."""
    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})

    for item_key, quantity in bag.items():
        if '-' in item_key:
            product_id, variant_id = item_key.split('-')
            product = get_object_or_404(Product, printful_id=product_id, variant_id=variant_id)
        else:
            product_id = item_key
            product = Product.objects.filter(printful_id=product_id).first()
            if not product:
                continue

        subtotal = quantity * product.price
        total += subtotal
        product_count += quantity

        bag_items.append({
            'product_id': product_id,
            'variant_id': variant_id if '-' in item_key else None,
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
            'size': product.size,
        })

    # Ensure grand_total is defined even if there are no items in the bag
    grand_total = total  # Update this if you have additional calculations for grand_total like delivery fees

    context = {
        'bag_items': bag_items,
        'total': total,
        'grand_total': grand_total,  
        'product_count': product_count,
    }

    return context
