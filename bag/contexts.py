from decimal import Decimal
from django.conf import settings
from products.models import Product

def bag_contents(request):
    """ Retrieve the bag and calculate totals """
    bag = request.session.get('bag', {})
    bag_items = []
    total = Decimal(0)
    
    for product_id, quantity in bag.items():
        product = Product.objects.get(printful_id=product_id)
        subtotal = product.price * quantity  # Calculate the subtotal for this item
        total += subtotal  # Add to total
        bag_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,  # Pass subtotal to the template
        })

    context = {
        'bag_items': bag_items,
        'total': total,
    }
    
    return context
