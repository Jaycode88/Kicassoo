# home/views.py
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render
from .forms import ContactForm

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data and send the email
            send_mail(
                subject=f"Contact Form Submission from {form.cleaned_data['name']}",
                message=form.cleaned_data['message'],
                from_email=form.cleaned_data['email'],
                recipient_list=[settings.EMAIL_HOST_USER],
            )
            # Return JSON with a success message
            return JsonResponse({
                "success": True,
                "message": "Your message has been sent successfully!"
            })
        else:
            # Return JSON with an error message
            return JsonResponse({
                "success": False,
                "message": "There was an error in your form submission. Please check your entries and try again."
            }, status=400)

    # Catch-all return if the request is not POST
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