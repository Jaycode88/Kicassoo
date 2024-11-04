from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation_email(order):
    """Sends an order confirmation email to the customer."""
    order_items = order.orderitem_set.all()  # Fetch all items associated with the order
    
    # Calculate the order total with all items
    total = sum(item.quantity * item.price for item in order_items)
    
    # Create the context with order details, including item details
    context = {
        'order': order,
        'order_items': order_items,
        'total': total,
    }
    
    subject = f"Order Confirmation - {order.id}"
    message = render_to_string('emails/order_confirmation.html', context)
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
        html_message=message  # Ensure the email is sent as HTML
    )
