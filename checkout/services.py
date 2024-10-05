from django.conf import settings

PRINTFUL_API_URL = 'https://api.printful.com/orders'

def prepare_printful_order_data(order):
    items = []
    for item in order.items.all():
        items.append({
            'sync_variant_id': item.printful_variant_id,
            'quantity': item.quantity,
            'retail_price': str(item.price),
        })

    return {
        'recipient': {
            'name': order.full_name,
            'address1': order.street_address1,
            'address2': order.street_address2 or '',
            'city': order.town_or_city,
            'state_code': order.county or '',
            'zip': order.postcode,
            'country_code': order.country.code,
            'phone': order.phone_number,
            'email': order.email,
        },
        'items': items,
        'shipping': 'STANDARD',
    }

