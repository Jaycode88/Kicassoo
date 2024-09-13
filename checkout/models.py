from django.db import models
import uuid
from django.conf import settings
from decimal import Decimal
from django_countries.fields import CountryField

from products.models import Product

class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    postcode = models.CharField(max_length=10, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    country = CountryField(default="GB")  # Default to United Kingdom
    date = models.DateTimeField(auto_now_add=True)

    # Cost-related fields
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)

    # Printful-specific fields
    printful_order_id = models.CharField(max_length=50, null=True, blank=True)  # Store Printful order ID
    estimated_shipping_date = models.DateField(null=True, blank=True)  # Store estimated shipping date

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID.
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update the order total and grand total each time an item is added, updated, or removed.
        """
        self.order_total = self.items.aggregate(
            total=models.Sum(models.F('price') * models.F('quantity'))
        )['total'] or Decimal('0.00')
        
        # Update the grand total by adding delivery cost
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the save method to set the order number if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    # Printful-specific fields
    printful_product_id = models.CharField(max_length=50, null=True, blank=True)
    printful_variant_id = models.CharField(max_length=50, null=True, blank=True)
    estimated_shipping_date = models.DateField(null=True, blank=True)

    @property
    def lineitem_total(self):
        """
        Calculate the total for this line item.
        """
        if self.price is not None and self.quantity is not None:
            return self.quantity * self.price
        return Decimal('0.00')

    def save(self, *args, **kwargs):
        """
        Override save to update the order total when an OrderItem is created or updated.
        """
        super().save(*args, **kwargs)
        self.order.update_total()

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'
