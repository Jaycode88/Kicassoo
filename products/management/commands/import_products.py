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

                product_details = api.get_product_variants(item['id'])
                if not product_details or 'sync_variants' not in product_details:
                    print(f"No variants found for item: {item}")  # Debugging statement
                    continue

                variants = product_details['sync_variants']
                if not variants:
                    print(f"No valid variants found for item: {item}")  # Debugging statement
                    continue

                # Assuming you take the first variant for simplicity
                first_variant = variants[0]
                price = first_variant['retail_price']

                product, created = Product.objects.update_or_create(
                    printful_id=item['id'],
                    defaults={
                        'name': item['name'],
                        'image_url': item['thumbnail_url'],
                        'price': price,
                    }
                )
            except Exception as e:
                print(f"Error processing item {item}: {e}")  # Error handling and debugging

        self.stdout.write(self.style.SUCCESS('Successfully imported products from Printful'))
