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
    search_string = request.GET.get('str')
    thu = thulac.thulac(seg_only=True)
    words = thu.cut(search_string, text=True).split()
    q_object = Q()
    for word in words:
        q_object |= (Q(title__icontains=word) | Q(model__icontains=word))
    items = Product.objects.filter(q_object)
    print(len(items))
    paginator = Paginator(items, 60)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'search.html', {'products': products, 'search_string': search_string,
                                           'max_page': paginator.num_pages})


def get_filter_list(model, value):
    lst = list(model.values_list(value))
    counts = collections.Counter(lst)
    lst = sorted(set(lst), key=counts.get, reverse=True)

    if '' in lst:
        lst.remove('')
    if len(lst) == 1:
        return []
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
    if len(lst) == 1:
        return []

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


def price_range_filter(products, price_range):
    range = price_range.split('~')
    products = products.filter(price__gt=float(range[0]))
    products = products.filter(price__lte=float(range[1]))
    return products


def network_filter(products, net):
    if net == '全网通':
        products = products.filter(network_support__all_kind=True)
    elif net == '移动':
        products = products.filter(network_support__china_mobile=True)
    elif net == '联通':
        products = products.filter(network_support__china_unicom=True)
    elif net == '电信':
        products = products.filter(network_support__china_telecom=True)
    return products


def get_price_range_filter_list(products):
    max_price = products.order_by('-price')[0].price
    filter_list = []
    for i in range(int(max_price / 1000) + 1):
        filter_list.append(str(i * 1000) + '~' + str((i + 1) * 1000))
    return [filter_list[i:i + 8] for i in range(0, len(filter_list), 8)]


def get_network_filter_list(products):
    filter_list = []
    if products.filter(network_support__all_kind=True):
        filter_list.append('全网通')
    if products.filter(network_support__china_mobile=True):
        filter_list.append('移动')
    if products.filter(network_support__china_unicom=True):
        filter_list.append('联通')
    if products.filter(network_support__all_kind=True):
        filter_list.append('电信')
    if len(filter_list) <= 1:
        return []
    filter_list += [''] * (8 - len(filter_list) % 8)
    return [filter_list]


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
    price_range = request.GET.get('price_range')
    network_support = request.GET.get('network_support')
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
    if network_support:
        products = network_filter(products, network_support)
        filtered.append(('网络支持', 'network_support', network_support))
    if price_range:
        products = price_range_filter(products, price_range)
        filtered.append(('价格范围', 'price_range', price_range))
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
    if not network_support:
        filter_list.append(('网络支持', 'network_support', get_network_filter_list(products)))
    if not price_range:
        filter_list.append(('价格范围', 'price_range', get_price_range_filter_list(products)))
    if not color:
        filter_list.append(('机身颜色', 'color', get_filter_list(products, 'color')))
    if not platform:
        filter_list.append(('商城', 'platform', get_filter_list(products, 'platform')))

    return products, filtered, filter_list


def get_products_by_category(request, category):
    if category == '手机':
        return cellphone_filter(request)
    return None, None, None


def category_list_page(request):
    return render(request, 'categories.html')


def takeFirst(elem):
    return elem[0]


def products_filter(request, category):
    if not category:
        return category_list_page(request)
    page = request.GET.get('page')
    common = request.GET.get('common')
    sort_list = {'price': ('价格', request.GET.get('price')), 'score': ('评分', request.GET.get('score')),
                 'date': ('上市时间', request.GET.get('date')), 'comment_num': ('全网评论数', request.GET.get('comment_num'))}
    search_string = request.GET.get('str')
    url = request.get_full_path()
    sorted_list = []
    products, filtered, filter_list = get_products_by_category(request, category)
    if products is None:
        return page_not_found(request)

    if common is None:
        for name, value in sort_list.items():
            if value[1] is None:
                continue
            elif value[1] == 'up':
                sorted_list.append((url.index(name), name))
            else:
                sorted_list.append((url.index(name), '-' + name))
        sorted_list.sort(key=takeFirst)
        sorted_list = [i[1] for i in sorted_list]
        if len(sorted_list) > 0:
            products = products.order_by(*sorted_list)

    total_result = len(products)
    paginator = Paginator(products, 60)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    if search_string:
        search_string = search_string.upper()
        for product in products:
            l = len(search_string)
            if search_string in product.model.upper():
                model = product.model
                model_upper = model.upper()
                model_index = model_upper.index(search_string)
                product.model = model[:model_index] + '<em style="color: #c00;">' + model[model_index:model_index + l] + '</em>' + model[model_index + l:]
            if search_string in product.title.upper():
                title = product.title
                title_upper = title.upper()
                title_index = title_upper.index(search_string)
                product.title = title[:title_index] + '<em style="color: #c00;">' + title[title_index:title_index + l] + '</em>' + title[title_index + l:]


    return render(request, 'products_filter.html', {'products': products,
                                                    'max_page': paginator.num_pages, 'total_result': total_result,
                                                    'category': category, 'filter_list': filter_list,
                                                    'filtered': filtered if filtered else None,
                                                    'sort_list': sort_list, 'common': common})


def get_cellphone_detail(product):
    net = product.network_support
    network_support = ''
    if 'all_kind' in net:
        network_support = '全网通'
    else:
        if 'china_mobile' in net:
            network_support += '移动'
        if 'china_unicom' in net:
            network_support += '联通'
        if 'china_telecom' in net:
            network_support += '电信'
    return [
        [('品牌', product.brand), ('上市时间', product.date), ('网络支持', network_support)],
        [('操作系统', product.os), ('屏幕尺寸', product.screen_size), ('分辨率', product.frequency)],
        [('CPU', product.cpu), ('存储内存', product.rom), ('运行内存', product.ram)],
        [('机身长度', product.height), ('机身宽度', product.width), ('机身厚度', product.thickness)],
        [('机身重量', product.weight), ('机身颜色', product.color)],
    ]


def products_detail(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    type_name = type(product).__name__
    detail_list = []
    if type_name == 'Cellphone':
        detail_list = get_cellphone_detail(product)
        model = Cellphone
    compare_list = compare_same_model(request, model, product_id)

    return render(request, 'products_detail.html', {'product': product, 'detail_list': detail_list, 'compare_list': compare_list})


def compare_same_model(request, model, product_id):
    product = model.objects.filter(id=product_id).first()
    products = model.objects.filter(brand=product.brand)
    products = products.filter(model=product.model)
    products = products.order_by('platform')
    return products
