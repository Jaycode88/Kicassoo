import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

PRINTFUL_API_URL = "https://api.printful.com"
PRINTFUL_API_KEY = os.environ.get('PRINTFUL_API_KEY') 

def list_printful_products():
    response = requests.get(
        f"{PRINTFUL_API_URL}/kicassoo/products",
        headers={"Authorization": f"Bearer {PRINTFUL_API_KEY}"}
    )
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    products = list_printful_products()
    for product in products['result']:
        print(f"Product ID: {product['id']}, Name: {product['name']}")