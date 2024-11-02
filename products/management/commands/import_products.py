from django.core.management.base import BaseCommand
from products.printful_service import PrintfulAPI
from products.models import Product
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Import products from Printful with variant handling and unique constraint checks'

    def handle(self, *args, **kwargs):
        api = PrintfulAPI()
        products = api.get_store_products()

        for item in products:
            try:
                # Get detailed product info, including variants
                product_details = api.get_product_details(item['id'])
                if not product_details:
                    continue

                # Loop through each variant to store them uniquely
                variants = product_details.get('sync_variants', [])
                for variant in variants:
                    sync_variant_id = variant['id']
                    price = variant['retail_price']
                    variant_id = variant['variant_id']
                    size = variant.get('size', '')  # Extract size from variant details

                    # Attempt to update or create with fallback delete if IntegrityError is raised
                    try:
                        # First, delete any existing product with the same printful_id and variant_id
                        Product.objects.filter(printful_id=item['id'], variant_id=variant_id).delete()
                        
                        # Now, create or update the product
                        product, created = Product.objects.update_or_create(
                            printful_id=item['id'],
                            variant_id=variant_id,
                            defaults={
                                'name': item['name'],
                                'image_url': item['thumbnail_url'],
                                'price': price,
                                'sync_variant_id': sync_variant_id,
                                'size': size  # Save size to the model
                            }
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f"Created product variant: {product.name} (Variant ID: {variant_id})"))
                        else:
                            self.stdout.write(f"Updated existing product variant: {product.name} (Variant ID: {variant_id})")

                    except IntegrityError as e:
                        self.stderr.write(f"Error processing variant {variant_id} for item {item}: {e}")

            except Exception as e:
                self.stderr.write(f"Error processing item {item}: {e}")

        self.stdout.write(self.style.SUCCESS('Successfully imported products and variants from Printful'))
