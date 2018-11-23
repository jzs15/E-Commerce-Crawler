from django.shortcuts import render
from mongoengine.queryset.visitor import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.models import Product
import segmentation


def index(request):
    return render(request, 'index.html')


def search(request):
    page = request.GET.get('page')
    sort = request.GET.get('sort')
    search_string = request.GET.get('str')
    words = segmentation.cut(search_string)
    q_object = Q()
    for word in words:
        q_object |= (Q(title__icontains=word) | Q(product_name__icontains=word))
    items = Product.objects.filter(q_object)

    if sort is '1':
        items = items.order_by('price')
    elif sort is '2':
        items = items.order_by('-price')
    else:
        sort = 0

    paginator = Paginator(items, 60)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    a = 0
    for pr in products:
        a += 1
        print(a, pr.shop_name, pr.product_id)

    return render(request, 'search.html', {'products': products, 'search_string': search_string,
                                           'max_page': paginator.num_pages, 'sort': sort})
