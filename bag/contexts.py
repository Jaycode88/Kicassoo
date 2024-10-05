from decimal import Decimal
from django.conf import settings
from products.models import Product

def bag_contents(request):
    bag = request.session.get('bag', {})
    bag_items = []
    total = 0

    for printful_id, quantity in bag.items():
        # Ensure printful_id is treated as a string
        product = Product.objects.get(printful_id=str(printful_id))
        total += quantity * product.price
        bag_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': quantity * product.price,
        })

    context = {
        'bag_items': bag_items,
        'total': total,
    }

    return context
