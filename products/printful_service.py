import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

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
            products = response.json().get('result', [])
            logger.info("Fetched Printful products: %s", products)  # Log products data for debugging
            return products
        logger.error("Failed to fetch products. Status code: %s", response.status_code)
        return []

    def get_product_details(self, product_id):
        """Get product details by ID from Printful"""
        response = requests.get(f'{self.base_url}/store/products/{product_id}', headers=self.get_headers())
        if response.status_code == 200:
            product_data = response.json().get('result', {})
            logger.info("Fetched Printful product details: %s", product_data)  # Log details for inspection
            return product_data
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
        """Send order to Printful with improved debugging and address verification"""
        logger.info("Creating draft order with Printful...")

        order_data['confirm'] = confirm

        # Log address1 specifically for troubleshooting
        address1 = order_data['recipient'].get('address1') or order_data['recipient'].get('address_line_1', '')
        if not address1:
            logger.error("Critical: Missing address1 in recipient data. Order data: %s", order_data)
            raise ValueError("address1 is required for Printful orders and cannot be empty.")
        
        # Ensure address1 is explicitly set in recipient data
        order_data['recipient']['address1'] = address1
        logger.info("Recipient data with confirmed address1 field: %s", order_data['recipient'])

        try:
            response = requests.post(f"{self.base_url}/orders", json=order_data, headers=self.get_headers())
            response.raise_for_status()  # Raises HTTPError if the status is 4xx/5xx
            logger.info("Order successfully created with response: %s", response.json())
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Detailed error logging for HTTP errors from Printful
            logger.error("HTTP Error from Printful. Status Code: %s, Response: %s", response.status_code, response.json())
            return None
        except requests.exceptions.RequestException as e:
            # Logs other request-related errors
            logger.error("Request error when creating order with Printful: %s", e)
            return None
