from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category
from django.db.models import Min


def product_list(request):
    """ A view to show all products, including sorting and search queries """

    # Get unique products by selecting the first variant for each `printful_id`
    products = Product.objects.values('printful_id').annotate(id=Min('id'))

    # Retrieve the Product objects for each unique `printful_id`
    products = Product.objects.filter(id__in=[product['id'] for product in products])

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
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].replace('+', ' ').split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

            # Check for no results after category filtering
            if not products.exists():
                messages.warning(request, "No products found for the selected category or categories.")
                return redirect(reverse('product_list'))

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('product_list'))

            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

            # Handle empty search results
            if not products.exists():
                messages.warning(request, "Your search returned no results.")
                return redirect(reverse('product_list'))

    # Check if sorting or filtering results in an empty product list
    if not products.exists():
        messages.warning(request, "No products match the current sorting and filtering options.")

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/product_list.html', context)


def product_detail(request, printful_id):
    product_variants = Product.objects.filter(printful_id=printful_id)  # All variants of this product
    return render(request, 'products/product_detail.html', {'product_variants': product_variants})
