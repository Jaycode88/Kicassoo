from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_order_confirmation_email(order):
     # Calculate the totals
    items_total = order.order_total
    delivery_cost = order.delivery_cost
    grand_total_with_delivery = order.grand_total

    # Render the email template with context
    email_subject = f"Order Confirmation - {order.order_number}"
    email_body = render_to_string('emails/order_confirmation.html', {
        'order': order,
        'order_items': order.items.all(),  # include all items for details
        'items_total': items_total,
        'delivery_cost': delivery_cost,
        'grand_total_with_delivery': grand_total_with_delivery,
    })
    
    # Send the email
    send_mail(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
        html_message=email_body
    )
