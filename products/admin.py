from django.contrib import admin
from .models import Product, Category


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'printful_id', 'price', 'description', 'category')
    search_fields = ('name', 'printful_id')
    list_filter = ('price', 'category')
    readonly_fields = ('printful_id',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
