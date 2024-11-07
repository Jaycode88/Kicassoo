from .forms import ContactForm

def contact_form(request):
    """Add the contact form to all templates."""
    return {
        'contact_form': ContactForm()
    }
