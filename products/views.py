from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.db.models import Q
from .models import Product

def product_list(request):
    """ A view to show all products ,including sorting and search queries """

    products = Product.objects.all()
    query = None

    if request.GET:
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('product_list'))

            Queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(Queries)

            # Handle empty search results
            if not products.exists():
                messages.warning(request, "Your search returned no results.")

    context = {
        'products': products,
        'search_term': query,
    }

    return render(request, 'products/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})
