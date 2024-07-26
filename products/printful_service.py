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
            'Authorization': f'Bearer {self.api_key}'
        }

    def get_store_products(self):
        response = requests.get(f'{self.base_url}/store/products', headers=self.get_headers())
        print(response.status_code, response.json())  # Debugging
        if response.status_code == 200:
            return response.json()['result']
        return []

    def get_product_details(self, product_id):
        response = requests.get(f'{self.base_url}/store/products/{product_id}', headers=self.get_headers())
        print(response.status_code, response.json())  # Debugging
        if response.status_code == 200:
            return response.json()['result']
        return {}
