from django.core.management.base import BaseCommand
from products.printful_service import PrintfulAPI
from products.models import Product

class Command(BaseCommand):
    help = 'Import products from Printful'

    def handle(self, *args, **kwargs):
        api = PrintfulAPI()
        products = api.get_store_products()

        for item in products:
            try:
                print(f"Processing item: {item}")  # Debugging statement

                # Get product details (with variants)
                product_details = api.get_product_details(item['id'])
                if not product_details:
                    print(f"No details found for item: {item}")  # Debugging statement
                    continue

                # Get the first variant and its details
                variants = product_details.get('sync_variants', [])
                if not variants:
                    print(f"No valid variants found for item: {item}")  # Debugging statement
                    continue

                first_variant = variants[0]
                price = first_variant['retail_price']
                variant_id = first_variant['variant_id']  # Extract the variant_id

                # Update or create product with correct data
                product, created = Product.objects.update_or_create(
                    printful_id=item['id'],  # Save the product's printful_id
                    defaults={
                        'name': item['name'],
                        'image_url': item['thumbnail_url'],
                        'price': price,
                        'variant_id': variant_id,  # Ensure variant_id is saved
                    }
                )
                print(f"Product {'created' if created else 'updated'}: {product.name}")
            
            except Exception as e:
                print(f"Error processing item {item}: {e}")  # Error handling and debugging

        self.stdout.write(self.style.SUCCESS('Successfully imported products from Printful'))
