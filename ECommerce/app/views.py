from django.shortcuts import render
from mongoengine.queryset.visitor import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.models import *
import segmentation
import collections


def index(request):
    return render(request, 'index.html')


def search(request):
    page = request.GET.get('page')
    sort1 = request.GET.get('sort1')
    search_string = request.GET.get('str')
    words = segmentation.cut(search_string)
    q_object = Q()
    for word in words:
        q_object |= (Q(title__icontains=word) | Q(product_name__icontains=word))
    items = Product.objects.filter(q_object)

    if sort1 is '1':
        items = items.order_by('price')
    elif sort1 is '2':
        items = items.order_by('-price')
    else:
        sort1 = 0

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
                                           'max_page': paginator.num_pages, 'sort1': sort1})


def get_filter_list(model, value):
    lst = list(model.values_list(value))
    counts = collections.Counter(lst)
    return sorted(set(lst), key=counts.get, reverse=True)


def products_filter(request):
    page = request.GET.get('page')
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    filtered = []
    filter_list = []
    products = Cellphone.objects.all()
    if brand is not None:
        products = products.filter(brand=brand)
        filtered.append(('品牌', 'brand', brand))
    else:
        filter_list.append(('品牌', 'brand', get_filter_list(products, 'brand')))

    total_result = len(products)
    paginator = Paginator(products, 60)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'products_filter.html', {'products': products,
                                                    'max_page': paginator.num_pages, 'total_result': total_result,
                                                    'filter_list': filter_list,
                                                    'filtered': filtered if filtered else None})


def compare(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    return render(request, 'compare.html', {'product': product, 'items': product.items})
