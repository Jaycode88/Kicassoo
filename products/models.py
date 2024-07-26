from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    printful_id = models.CharField(max_length=255, unique=True)
    image_url = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
