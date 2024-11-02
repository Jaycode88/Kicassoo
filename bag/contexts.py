from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.conf import settings
from products.models import Product

def bag_contents(request):
    """Calculate and return bag contents."""
    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})

    for item_key, quantity in bag.items():
        # Check if item_key has a variant (product_id-variant_id format)
        if '-' in item_key:
            product_id, variant_id = item_key.split('-')
            product = get_object_or_404(Product, printful_id=product_id, variant_id=variant_id)
        else:
            # If no variant, just use product_id
            product_id = item_key
            product = Product.objects.filter(printful_id=product_id).first()

            if not product:
                continue  # Skip if no matching product is found

        # Calculate totals
        total += quantity * product.price
        product_count += quantity

        # Add item details to bag items list
        bag_items.append({
            'product_id': product_id,
            'variant_id': variant_id if '-' in item_key else None,
            'product': product,
            'quantity': quantity,
            'subtotal': quantity * product.price,
        })

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
    }

    return context