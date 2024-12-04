import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class PrintfulAPI:
    def __init__(self):
        self.api_key = settings.PRINTFUL_API_KEY
        if not self.api_key:
            raise ValueError(
                "No PRINTFUL_API_KEY found in environment variables")
        self.base_url = 'https://api.printful.com'

    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

    def get_store_products(self):
        """Get all products from Printful store"""
        response = requests.get(
            f'{self.base_url}/store/products', headers=self.get_headers())

        if response.status_code == 200:
            products = response.json().get('result', [])
            logger.info(
                "Fetched Printful products: %s", products)
            return products
        logger.error(
            "Failed to fetch products. Status code: %s",
            response.status_code)

        return []

    def get_product_details(self, product_id):
        """Get product details by ID from Printful."""
        try:
            response = requests.get(
                f'{self.base_url}/store/products/{product_id}',
                headers=self.get_headers())

            response.raise_for_status()
            product_data = response.json().get('result', {})
            logger.info(
                "Fetched Printful product details successfully for "
                "product ID %s.",
                product_id
            )

            return product_data
        except requests.exceptions.RequestException as e:
            logger.error(
                "Failed to fetch product details for product ID %s. Error: %s",
                product_id, e)

            return {}

    def get_shipping_rates(self, cart_items, destination):
        """Fetch shipping rates based on cart items and destination."""
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
            response = requests.post(url,
                                     json=data, headers=self.get_headers())
            response.raise_for_status()
            shipping_rates = response.json().get('result', [])
            logger.info("Fetched shipping rates successfully.")
            return shipping_rates
        except requests.exceptions.RequestException as e:
            logger.error("Error fetching shipping rates: %s", e)
            return None

    def create_order(self, order_data, confirm=False):
        """Send order to Printful, ensuring address requirements are met."""
        logger.info("Attempting to create order with Printful...")

        # Log the initial order data
        logger.debug("Initial order data: %s", order_data)

        order_data['confirm'] = confirm

        # Ensure 'address1' is provided in recipient data
        address1 = (
            order_data['recipient'].get('address1') or
            order_data['recipient'].get('address_line_1', '')
        )
        if not address1:
            logger.error(
                "Missing address1 in recipient data. "
                "Cannot proceed with order creation. Recipient data: %s",
                order_data['recipient']
            )
            raise ValueError(
                "address1 is required for Printful orders and cannot be empty."
            )

        order_data['recipient']['address1'] = address1

        # Log the final payload before making the API call
        logger.debug("Final order data to be sent to Printful: %s", order_data)

        try:
            response = requests.post(
                f"{self.base_url}/orders",
                json=order_data,
                headers=self.get_headers()
            )

            # Log the full response content for debugging
            logger.debug("Printful API response: %s", response.text)

            response.raise_for_status()
            order_response = response.json()

            logger.info(
                "Order successfully created with Printful. Order ID: %s",
                order_response.get('id')
            )
            return order_response

        except requests.exceptions.HTTPError as e:
            # Log detailed HTTP errors from Printful
            logger.error(
                "HTTP error while creating order with Printful. "
                "Status: %s, Response: %s, Error: %s",
                response.status_code, response.text, e
            )
            return None

        except requests.exceptions.RequestException as e:
            logger.error(
                "Error creating order with Printful: %s",
                e
            )
            return None
