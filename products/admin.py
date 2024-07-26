from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'printful_id', 'price', 'description')
    search_fields = ('name', 'printful_id')
    list_filter = ('price',)
    readonly_fields = ('printful_id',)  # Assuming you want to make printful_id read-only

admin.site.register(Product, ProductAdmin)
