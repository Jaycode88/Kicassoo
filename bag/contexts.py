from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product
import requests

def get_shipping_rates(cart_items, destination):
    url = 'https://api.printful.com/shipping/rates'
    headers = {
        'Authorization': f'Bearer {settings.PRINTFUL_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'recipient': {
            'country_code': destination['country_code'],
            'city': destination['city'],
            'address1': destination['address1'],
            'zip': destination['postcode'],
        },
        'items': cart_items
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['result']
    else:
        return None

def bag_contents(request):
    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})
    destination = {
        'country_code': 'GB',     # Country code for the UK
        'city': 'London',         # Default city
        'address1': '123 Default St', # Default address
        'postcode': 'EC1A 1BB'    # Default postcode
    }

    for item_id, quantity in bag.items():
        product = get_object_or_404(Product, pk=item_id)
        total += quantity * product.price
        product_count += quantity
        bag_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'product': product,
            'printful_id': product.printful_id,  # Using printful_id for shipping calculation
        })

    cart_items = [{'external_variant_id': item['printful_id'], 'quantity': item['quantity']} for item in bag_items]
    shipping_rates = get_shipping_rates(cart_items, destination)
    
    if shipping_rates:
        delivery = min(rate['rate'] for rate in shipping_rates)
    else:
        delivery = 0  # Default to 0 if no rates are found

    grand_total = delivery + total

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'grand_total': grand_total,
    }

    return context
