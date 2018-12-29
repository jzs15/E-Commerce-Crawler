from django.shortcuts import render, render_to_response
from mongoengine.queryset.visitor import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.models import *
import segmentation
import collections


def index(request):
    return render(request, 'index.html')


def page_not_found(request):
    return render_to_response('404.html')


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


def get_products_by_category(category):
    if category == '手机':
        return Cellphone.objects.all()
    return None


def category_list_page(request):
    return render(request, 'products_filter.html')


def products_filter(request, category):
    if not category:
        return category_list_page(request)
    page = request.GET.get('page')
    platform = request.GET.get('platform')
    brand = request.GET.get('brand')
    common = request.GET.get('common')
    sort_list = {'price': ('价格', request.GET.get('price')), 'score': ('评分', request.GET.get('score')),
                 'date': ('上市时间', request.GET.get('date')), 'comment_num': ('全网评论数', request.GET.get('comment_num'))}
    filtered = list()
    filter_list = list()
    sorted_list = list()
    products = get_products_by_category(category)
    if products is None:
        return page_not_found(request)

    if brand:
        products = products.filter(brand=brand)
        filtered.append(('品牌', 'brand', brand))

    if platform:
        products = products.filter(platform=platform)
        filtered.append(('商城', 'platform', platform))

    if not brand:
        filter_list.append(('品牌', 'brand', get_filter_list(products, 'brand')))
    if not platform:
        filter_list.append(('商城', 'platform', get_filter_list(products, 'platform')))


    if common is None:
        for name, value in sort_list.items():
            if value[1] is None:
                continue
            elif value[1] == 'up':
                sorted_list.append(name)
            else:
                sorted_list.append('-' + name)
        products = products.order_by(*sorted_list)


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
                                                    'filter_list': filter_list, 'filtered': filtered if filtered else None,
                                                    'sort_list': sort_list, 'common': common})


def compare(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    return render(request, 'compare.html', {'product': product, 'items': product.items})
