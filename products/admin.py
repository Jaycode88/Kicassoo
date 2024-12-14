from django.contrib import admin
from .models import Product, Category


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'printful_id', 'price', 'category', 'intro_description', 'details')
    search_fields = ('name', 'printful_id')
    list_filter = ('price', 'category')
    readonly_fields = ('printful_id',)
    fields = (
        'name', 
        'printful_id', 
        'variant_id', 
        'sync_variant_id', 
        'image_url', 
        'price', 
        'description',
        'category', 
        'size'
    )


admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
