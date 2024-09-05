from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category

def product_list(request):
    """ A view to show all products ,including sorting and search queries """

    products = Product.objects.all()
    query = None
    category = None
    categories = None
    sort = None
    direction = None
    

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sorttkey ='lower_name'
                products = products.annotate(lower_name=Lower('name'))
        
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)
        
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
    
    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': category,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/product_list.html', context)

def product_detail(request, printful_id):
    product = get_object_or_404(Product, printful_id=printful_id)
    return render(request, 'products/product_detail.html', {'product': product})
