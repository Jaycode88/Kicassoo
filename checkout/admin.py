from django.contrib import admin
from .models import Order, OrderItem

class OrderItemAdminInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = (
        'product', 'quantity', 'price', 'printful_product_id', 
        'printful_variant_id', 'estimated_shipping_date'
    )
    can_delete = False  # Disable deletion of OrderItems
    extra = 0  # Removes any empty inline forms for new OrderItems

class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderItemAdminInline,)

    readonly_fields = (
        'order_number', 'date', 'delivery_cost', 'order_total', 'grand_total',
        'stripe_payment_intent_id', 'printful_order_id', 'estimated_shipping_date', 'country'
    )

    fields = (
        'order_number', 'full_name', 'email', 'phone_number',
        'postcode', 'town_or_city', 'street_address1', 'street_address2', 
        'county', 'country', 'date', 'delivery_cost', 'order_total', 'grand_total',
        'stripe_payment_intent_id', 'printful_order_id', 'payment_status', 'estimated_shipping_date'
    )

    list_display = ('order_number', 'full_name', 'email', 'grand_total', 'date')
    ordering = ('-date',)

admin.site.register(Order, OrderAdmin)
