import requests
from django.conf import settings


class PrintfulAPI:
    def __init__(self):
        self.api_key = settings.PRINTFUL_API_KEY
        if not self.api_key:
            raise ValueError("No PRINTFUL_API_KEY found in environment variables")
        self.base_url = 'https://api.printful.com'

    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

    def get_store_products(self):
        """Get all products from Printful store"""
        response = requests.get(f'{self.base_url}/store/products', headers=self.get_headers())
        if response.status_code == 200:
            return response.json().get('result', [])
        return []

    def get_product_details(self, product_id):
        """Get product details by ID from Printful"""
        response = requests.get(f'{self.base_url}/store/products/{product_id}', headers=self.get_headers())
        if response.status_code == 200:
            return response.json().get('result', {})
        return {}

    def get_shipping_rates(self, cart_items, destination):
        """Fetch shipping rates based on cart items and destination"""
        url = f'{self.base_url}/shipping/rates'
        data = {
            'recipient': {
                'country_code': destination['country_code'],
                'city': destination['city'],
                'address1': destination['address1'],
                'zip': destination['postcode'],
            },
            'items': cart_items
        }

        try:
            response = requests.post(url, json=data, headers=self.get_headers())
            response.raise_for_status()  # Will raise an exception for HTTP error codes
            return response.json().get('result', [])
        except requests.exceptions.RequestException as e:
            # Handle and log errors more effectively
            print(f"Error fetching shipping rates: {e}")
            return None

    def create_order(self, order_data, confirm=False):
        print("Creating draft order with Printful...")
        print("Order Data:", order_data)  # Log order data for debugging
        url = f'{self.base_url}/orders'
        order_data['confirm'] = confirm

        for item in order_data.get('items', []):
            item['sync_variant_id'] = item.pop('variant_id', None)

        try:
            response = requests.post(url, json=order_data, headers=self.get_headers())
            response.raise_for_status()
            print("Order created successfully:", response.json())
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating order: {e}")
            return None
