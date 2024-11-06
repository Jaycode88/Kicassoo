from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_order_confirmation_email(order):
    # Render the email template with order context
    email_subject = f"Order Confirmation - {order.order_number}"
    email_body = render_to_string('emails/order_confirmation.html', {
        'order': order,
        'order_items': order.items.all(),  # get related items for details
    })
    
    # Send the email
    send_mail(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
        html_message=email_body  # To send HTML emails
    )
