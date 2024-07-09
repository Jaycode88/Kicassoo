from django.shortcuts import render

def index(request):
    """A view that displays the index page of the site."""
    
    return render(request, 'home/index.html')

def about(request):
    return render(request, 'home/about.html')

def events(request):
    return render(request, 'home/events.html')