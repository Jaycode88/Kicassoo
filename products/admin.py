from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'printful_id', 'price', 'image_url')
    search_fields = ('name', 'printful_id')

# Alternatively, the standard way:
# admin.site.register(Product, ProductAdmin)
