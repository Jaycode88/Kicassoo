from django.conf import settings
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

PRINTFUL_API_URL = 'https://api.printful.com'

def prepare_printful_order_data(order):
    items = []
    for item in order.items.all():
        items.append({
            'sync_variant_id': item.product.printful_variant_id,
            'quantity': item.quantity,
        })

    order_data = {
        'recipient': {
            'name': order.full_name,
            'address1': order.street_address1,  # Ensure correct mapping
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

    # Log prepared data with explicit `address1` check
    logger.info("Prepared Printful order data with address1 verification: %s", order_data)
    return order_data

