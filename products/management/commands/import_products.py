from django.core.management.base import BaseCommand
from products.printful_service import PrintfulAPI
from products.models import Product
from django.db import IntegrityError


class Command(BaseCommand):
    help = (
        'Import products from Printful with variant handling '
        'and unique constraint checks'
    )

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
                    size = variant.get('size')

                    try:
                        # Del existing product with same printful + variant_id
                        Product.objects.filter(
                            printful_id=item['id'],
                            variant_id=variant_id
                        ).delete()

                        # Create or update the product with size information
                        product, created = Product.objects.update_or_create(
                            printful_id=item['id'],
                            variant_id=variant_id,
                            defaults={
                                'name': item['name'],
                                'image_url': item['thumbnail_url'],
                                'price': price,
                                'sync_variant_id': sync_variant_id,
                                'size': size,  # Save size for each variant
                            }
                        )

                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Created product variant: {product.name} "
                                    f"(Variant ID: {variant_id}, Size: {size})"
                                )
                            )
                        else:
                            self.stdout.write(
                                f"Updated existing product variant: "
                                f"{product.name} "
                                f"(Variant ID: {variant_id}, "
                                f"Size: {size})"
                            )

                    except IntegrityError as e:
                        self.stderr.write(
                            f"Error processing variant {variant_id} "
                            f"for item {item}: "
                            f"{e}"
                        )

            except Exception as e:
                self.stderr.write(
                    f"Error processing item {item}: {e}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully imported products and variants from Printful'
            )
        )
