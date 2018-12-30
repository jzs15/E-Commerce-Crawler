from django.shortcuts import render, render_to_response
from mongoengine.queryset.visitor import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.models import *
import collections
import thulac


def index(request):
    return render(request, 'index.html')


def page_not_found(request):
    return render_to_response('404.html')


def search(request):
    page = request.GET.get('page')
    sort1 = request.GET.get('sort1')
    search_string = request.GET.get('str')
    thu = thulac.thulac()
    words = thu.cut(search_string, text=True)
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
    lst = sorted(set(lst), key=counts.get, reverse=True)

    if '' in lst:
        lst.remove('')
    if '其他' in lst:
        lst.remove('其他')
        lst.append('其他')
    if lst:
        lst += [''] * (8 - len(lst) % 8)
    return [lst[i:i + 8] for i in range(0, len(lst), 8)]


def get_filter_list_sorted(model, value):
    lst = list(set(list(model.values_list(value))))
    if '' in lst:
        lst.remove('')

    mb = []
    gb = []
    tb = []
    etc = []
    for x in lst:
        if 'MB' in x and x[:-2].isnumeric():
            mb.append(int(x[:-2]))
        elif 'GB' in x and x[:-2].isnumeric():
            gb.append(int(x[:-2]))
        elif 'TB' in x and x[:-2].isnumeric():
            gb.append(int(x[:-2]))
        else:
            etc.append(x)
    mb.sort(reverse=True)
    gb.sort(reverse=True)
    lst = [str(x) + 'TB' for x in tb] + [str(x) + 'GB' for x in gb] + [str(x) + 'MB' for x in mb] + etc

    if '其他' in lst:
        lst.remove('其他')
        lst.append('其他')
    if lst:
        lst += [''] * (8 - len(lst) % 8)
    return [lst[i:i + 8] for i in range(0, len(lst), 8)]


def get_products_by_category(request, category):
    if category == '手机':
        return cellphone_filter(request)
    return None


def get_products_by_search(products, search_string):
    if not search_string:
        return products
    thu = thulac.thulac(seg_only=True)
    words = thu.cut(search_string, text=True)
    words = words.split()
    q_object = Q()
    for word in words:
        q_object |= (Q(title__icontains=word) | Q(model__icontains=word))
    return products.filter(q_object)


def cellphone_filter(request):
    products = Cellphone.objects.all()
    filtered = []
    filter_list = []
    products = get_products_by_search(products, request.GET.get('str'))
    color = request.GET.get('color')
    platform = request.GET.get('platform')
    brand = request.GET.get('brand')
    os = request.GET.get('os')
    cpu = request.GET.get('cpu')
    ram = request.GET.get('ram')
    rom = request.GET.get('rom')
    if brand:
        products = products.filter(brand=brand)
        filtered.append(('品牌', 'brand', brand))
    if os:
        products = products.filter(os=os)
        filtered.append(('操作系统', 'os', os))
    if cpu:
        products = products.filter(cpu=cpu)
        filtered.append(('CPU', 'cpu', cpu))
    if ram:
        products = products.filter(ram=ram)
        filtered.append(('RAM', 'ram', ram))
    if rom:
        products = products.filter(rom=rom)
        filtered.append(('ROM', 'rom', rom))
    if color:
        products = products.filter(color=color)
        filtered.append(('机身颜色', 'color', color))
    if platform:
        products = products.filter(platform=platform)
        filtered.append(('商城', 'platform', platform))

    if not brand:
        filter_list.append(('品牌', 'brand', get_filter_list(products, 'brand')))
    if not os:
        filter_list.append(('操作系统', 'os', get_filter_list(products, 'os')))
    if not cpu:
        filter_list.append(('CPU', 'cpu', get_filter_list(products, 'cpu')))
    if not ram:
        filter_list.append(('RAM', 'ram', get_filter_list_sorted(products, 'ram')))
    if not rom:
        filter_list.append(('ROM', 'rom', get_filter_list_sorted(products, 'rom')))
    if not color:
        filter_list.append(('机身颜色', 'color', get_filter_list(products, 'color')))
    if not platform:
        filter_list.append(('商城', 'platform', get_filter_list(products, 'platform')))

    return products, filtered, filter_list


def category_list_page(request):
    return render(request, 'categories.html')


def products_filter(request, category):
    if not category:
        return category_list_page(request)
    page = request.GET.get('page')
    common = request.GET.get('common')
    sort_list = {'price': ('价格', request.GET.get('price')), 'score': ('评分', request.GET.get('score')),
                 'date': ('上市时间', request.GET.get('date')), 'comment_num': ('全网评论数', request.GET.get('comment_num'))}
    sorted_list = []
    products, filtered, filter_list = get_products_by_category(request, category)
    if products is None:
        return page_not_found(request)

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
                                                    'category': category, 'filter_list': filter_list,
                                                    'filtered': filtered if filtered else None,
                                                    'sort_list': sort_list, 'common': common})


def compare(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    return render(request, 'compare.html', {'product': product, 'items': product.items})
