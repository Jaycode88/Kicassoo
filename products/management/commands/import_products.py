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
                # Get product details, including variants
                product_details = api.get_product_details(item['id'])
                if not product_details:
                    continue

                # Loop through each variant to store `sync_variant_id`
                variants = product_details.get('sync_variants', [])
                for variant in variants:
                    sync_variant_id = variant['id']  # This is `sync_variant_id` from Printful
                    price = variant['retail_price']
                    variant_id = variant['variant_id']  # Specific variant identifier

                    # Update or create each variant in your Product model
                    product, created = Product.objects.update_or_create(
                        printful_id=item['id'],
                        variant_id=variant_id,  # Ensure `variant_id` is unique per variant
                        defaults={
                            'name': item['name'],
                            'image_url': item['thumbnail_url'],
                            'price': price,
                        }
                    )
                    # Optionally, save `sync_variant_id` if not yet stored
                    product.sync_variant_id = sync_variant_id
                    product.save()

            except Exception as e:
                print(f"Error processing item {item}: {e}")

        self.stdout.write(self.style.SUCCESS('Successfully imported products from Printful'))