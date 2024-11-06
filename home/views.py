from django.shortcuts import render

def index(request):
    """A view that displays the index page of the site."""
    
    return render(request, 'home/index.html')

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