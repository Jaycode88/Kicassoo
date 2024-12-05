from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render
from .forms import ContactForm


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Extract form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Construct email subject and body
            subject = f"Contact Form Submission from {name}"
            body = (
                f"You have received a new message via the contact form.\n\n"
                f"Name: {name}\n"
                f"Email: {email}\n\n"
                f"Message:\n{message}"
            )

            # Send the email
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,  # To debug email issues
            )

            # Return success response
            return JsonResponse({
                "success": True,
                "message": "Your message has been sent successfully!"
            })
        else:
            # Return form validation errors
            return JsonResponse({
                "success": False,
                "message": (
                    "There was an error in your form submission. "
                    "Please check your entries and try again."
                )
            }, status=400)

    # Catch-all for non-POST requests
    return JsonResponse({
        "success": False,
        "message": "Invalid request method."
    }, status=400)


def index(request):
    contact_form = ContactForm()
    """A view that displays the index page of the site."""
    return render(request, 'home/index.html', {'contact_form': contact_form})


def about(request):
    return render(request, 'home/about.html')


def all_collections(request):
    return render(request, 'home/collections/all_collections.html')


def perfectmoments(request):
    return render(request, 'home/collections/perfectmoments.html')


def ropesofwisdom(request):
    return render(request, 'home/collections/ropesofwisdom.html')


def thekingdom(request):
    return render(request, 'home/collections/thekingdom.html')


def events(request):
    return render(request, 'home/events.html')

def custom_404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    """Custom 500 error handler"""
    return render(request, 'errors/500.html', status=500)

def terms_and_conditions(request):
    """View to render Terms and Conditions page."""
    return render(request, 'home/terms_and_conditions.html')


def privacy_policy(request):
    """View to render Privacy Policy page."""
    return render(request, 'home/privacy_policy.html')
