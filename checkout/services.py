import requests
from django.conf import settings

PRINTFUL_API_URL = 'https://api.printful.com/orders'

def prepare_printful_order_data(order):
    """
    Prepare the order data in the format that Printful's API expects.
    """
    items = []
    for item in order.items.all():
        items.append({
            'sync_variant_id': item.printful_variant_id,
            'quantity': item.quantity,
            'retail_price': str(item.price),  # Convert Decimal to string
        })

    return {
        'recipient': {
            'name': order.full_name,
            'address1': order.street_address1,
            'address2': order.street_address2 or '',
            'city': order.town_or_city,
            'state_code': order.county or '',  # Optional, depending on country
            'zip': order.postcode,
            'country_code': order.country.code,  # Use country code like 'GB' for UK
            'phone': order.phone_number,
            'email': order.email,
        },
        'items': items,
        'shipping': 'STANDARD',  # Or another shipping option if needed
    }


class PrintfulAPIClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or settings.PRINTFUL_API_KEY
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

    def create_order(self, order_data, confirm=False):
        """
        Sends the order data to Printful API to create an order.
        If confirm is False, the order will be created as a draft.
        """
        order_data['confirm'] = False  # Set confirm to False for draft orders or True for live orders N.B also need to change line 30 in views.py
        
        try:
            response = requests.post(PRINTFUL_API_URL, json=order_data, headers=self.headers)
            response.raise_for_status()
            return response.json()  # Return the JSON response from Printful
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")
        return None


    def get_order(self, printful_order_id):
        """
        Retrieves the details of an order from Printful.
        """
        try:
            response = requests.get(f'{PRINTFUL_API_URL}/{printful_order_id}', headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")
        return None
