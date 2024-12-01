from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    printful_id = models.CharField(max_length=255)
    variant_id = models.CharField(max_length=255)
    sync_variant_id = models.IntegerField()
    image_url = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey('Category',
                                 on_delete=models.SET_NULL,
                                 null=True, blank=True)

    size = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ('printful_id', 'variant_id')

    def __str__(self):
        return f"{self.name} ({self.size})"
