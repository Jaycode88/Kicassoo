import requests
from django.conf import settings

PRINTFUL_API_URL = 'https://api.printful.com/orders'

class PrintfulAPIClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or settings.PRINTFUL_API_KEY
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

    def create_order(self, order_data):
        """
        Sends the order data to Printful API to create an order.
        """
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
