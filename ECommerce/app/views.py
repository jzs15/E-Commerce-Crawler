from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.models import *
import collections
import segmentation

seg = segmentation.Segmentation()


def index(request):
    return render(request, 'index.html')


def page_not_found(request):
    return render_to_response('404.html')


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


def get_filter_list_data(model, value):
    lst = list(set(list(model.values_list(value))))
    if '' in lst:
        lst.remove('')
    if len(lst) == 1:
        return []

    mb = []
    gb = []
    tb = []
    for x in lst:
        if 'MB' in x and x[:-2].isnumeric():
            mb.append(int(x[:-2]))
        elif 'GB' in x and x[:-2].isnumeric():
            gb.append(int(x[:-2]))
        elif 'TB' in x and x[:-2].isnumeric():
            gb.append(int(x[:-2]))
    mb.sort(reverse=True)
    gb.sort(reverse=True)
    lst = [str(x) + 'TB' for x in tb] + [str(x) + 'GB' for x in gb] + [str(x) + 'MB' for x in mb]

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
    lst.sort(reverse=True)
    if '其他' in lst:
        lst.remove('其他')
        lst.append('其他')
    if lst:
        lst += [''] * (8 - len(lst) % 8)
    return [lst[i:i + 8] for i in range(0, len(lst), 8)]


def get_products_by_search(products, search_string):
    if not search_string:
        return products
    words = seg.cut(search_string)
    q_object = Q()
    for word in words:
        q_object &= (Q(title__icontains=word) | Q(model__icontains=word))
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
    if not products:
        return []
    max_price = products.order_by('-price')[0].price
    filter_list = []
    for i in range(int(max_price / 1000) + 1):
        filter_list.append(str(i * 1000) + '~' + str((i + 1) * 1000))
    if filter_list:
        filter_list += [''] * (8 - len(filter_list) % 8)
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


def product_filter(request):
    products = Product.objects.all()
    products = get_products_by_search(products, request.GET.get('str'))
    platform = request.GET.get('platform')
    price_range = request.GET.get('price_range')
    filtered = []
    filter_list = []

    if price_range:
        products = price_range_filter(products, price_range)
        filtered.append(('价格范围', 'price_range', price_range))
    if platform:
        products = products.filter(platform=platform)
        filtered.append(('商城', 'platform', platform))

    if not price_range:
        filter_list.append(('价格范围', 'price_range', get_price_range_filter_list(products)))
    if not platform:
        filter_list.append(('商城', 'platform', get_filter_list(products, 'platform')))
    return products, filtered, filter_list


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
        filter_list.append(('RAM', 'ram', get_filter_list_data(products, 'ram')))
    if not rom:
        filter_list.append(('ROM', 'rom', get_filter_list_data(products, 'rom')))
    if not network_support:
        filter_list.append(('网络支持', 'network_support', get_network_filter_list(products)))
    if not price_range:
        filter_list.append(('价格范围', 'price_range', get_price_range_filter_list(products)))
    if not color:
        filter_list.append(('机身颜色', 'color', get_filter_list(products, 'color')))
    if not platform:
        filter_list.append(('商城', 'platform', get_filter_list(products, 'platform')))

    return products, filtered, filter_list


def refrigerator_filter(request):
    products = Refrigerator.objects.all()
    filtered = []
    filter_list = []
    products = get_products_by_search(products, request.GET.get('str'))
    color = request.GET.get('color')
    platform = request.GET.get('platform')
    brand = request.GET.get('brand')
    weather = request.GET.get('weather')
    rank = request.GET.get('rank')
    method = request.GET.get('method')
    price_range = request.GET.get('price_range')
    if brand:
        products = products.filter(brand=brand)
        filtered.append(('品牌', 'brand', brand))
    if weather:
        products = products.filter(weather=weather)
        filtered.append(('气候类型', 'weather', weather))
    if rank:
        products = products.filter(rank=rank)
        filtered.append(('能效等级', 'rank', rank))
    if method:
        products = products.filter(method=method)
        filtered.append(('开门方式', 'method', method))
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
    if not weather:
        filter_list.append(('气候类型', 'weather', get_filter_list(products, 'weather')))
    if not rank:
        filter_list.append(('能效等级', 'rank', get_filter_list(products, 'rank')))
    if not method:
        filter_list.append(('开门方式', 'method', get_filter_list(products, 'method')))
    if not price_range:
        filter_list.append(('价格范围', 'price_range', get_price_range_filter_list(products)))
    if not color:
        filter_list.append(('机身颜色', 'color', get_filter_list(products, 'color')))
    if not platform:
        filter_list.append(('商城', 'platform', get_filter_list(products, 'platform')))

    return products, filtered, filter_list


def computer_filter(request, model):
    products = model.objects.all()
    filtered = []
    filter_list = []
    products = get_products_by_search(products, request.GET.get('str'))
    color = request.GET.get('color')
    platform = request.GET.get('platform')
    brand = request.GET.get('brand')
    os = request.GET.get('os')
    core = request.GET.get('core')
    cpu = request.GET.get('cpu')
    ram = request.GET.get('ram')
    hdd = request.GET.get('hdd')
    ssd = request.GET.get('ssd')
    graphic_card = request.GET.get('graphic_card')
    price_range = request.GET.get('price_range')
    if brand:
        products = products.filter(brand=brand)
        filtered.append(('品牌', 'brand', brand))
    if os:
        products = products.filter(os=os)
        filtered.append(('操作系统', 'os', os))
    if cpu:
        products = products.filter(cpu=cpu)
        filtered.append(('CPU', 'cpu', cpu))
    if core:
        products = products.filter(core=core)
        filtered.append(('核心数', 'core', core))
    if ram:
        products = products.filter(ram=ram)
        filtered.append(('内存', 'ram', ram))
    if hdd:
        products = products.filter(hdd=hdd)
        filtered.append(('机械硬盘', 'hdd', hdd))
    if ssd:
        products = products.filter(ssd=ssd)
        filtered.append(('固态硬盘', 'ssd', ssd))
    if graphic_card:
        products = products.filter(graphic_card=graphic_card)
        filtered.append(('显卡', 'graphic_card', graphic_card))
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
    if not core:
        filter_list.append(('核心数', 'core', get_filter_list_sorted(products, 'core')))
    if not ram:
        filter_list.append(('内存', 'ram', get_filter_list_data(products, 'ram')))
    if not hdd:
        filter_list.append(('机械硬盘', 'hdd', get_filter_list_data(products, 'hdd')))
    if not ssd:
        filter_list.append(('固态硬盘', 'ssd', get_filter_list_data(products, 'ssd')))
    if not graphic_card:
        filter_list.append(('显卡', 'graphic_card', get_filter_list(products, 'graphic_card')))
    if not price_range:
        filter_list.append(('价格范围', 'price_range', get_price_range_filter_list(products)))
    if not color:
        filter_list.append(('机身颜色', 'color', get_filter_list(products, 'color')))
    if not platform:
        filter_list.append(('商城', 'platform', get_filter_list(products, 'platform')))

    return products, filtered, filter_list


def television_filter(request):
    products = Television.objects.all()
    filtered = []
    filter_list = []
    products = get_products_by_search(products, request.GET.get('str'))
    color = request.GET.get('color')
    platform = request.GET.get('platform')
    brand = request.GET.get('brand')
    tv_category = request.GET.get('tv_category')
    os = request.GET.get('os')
    ram = request.GET.get('ram')
    rom = request.GET.get('rom')
    price_range = request.GET.get('price_range')

    if brand:
        products = products.filter(brand=brand)
        filtered.append(('品牌', 'brand', brand))
    if tv_category:
        products = products.filter(tv_category=tv_category)
        filtered.append(('电视类型', 'tv_category', tv_category))
    if os:
        products = products.filter(os=os)
        filtered.append(('操作系统', 'os', os))
    if ram:
        products = products.filter(ram=ram)
        filtered.append(('RAM', 'ram', ram))
    if rom:
        products = products.filter(rom=rom)
        filtered.append(('ROM', 'rom', rom))
    if price_range:
        products = price_range_filter(products, price_range)
        filtered.append(('价格范围', 'price_range', price_range))
    if color:
        products = products.filter(color=color)
        filtered.append(('颜色', 'color', color))
    if platform:
        products = products.filter(platform=platform)
        filtered.append(('商城', 'platform', platform))

    if not brand:
        filter_list.append(('品牌', 'brand', get_filter_list(products, 'brand')))
    if not tv_category:
        filter_list.append(('电视类型', 'tv_category', get_filter_list(products, 'tv_category')))
    if not os:
        filter_list.append(('操作系统', 'os', get_filter_list(products, 'os')))
    if not ram:
        filter_list.append(('RAM', 'ram', get_filter_list_data(products, 'ram')))
    if not rom:
        filter_list.append(('ROM', 'rom', get_filter_list_data(products, 'rom')))
    if not price_range:
        filter_list.append(('价格范围', 'price_range', get_price_range_filter_list(products)))
    if not color:
        filter_list.append(('颜色', 'color', get_filter_list(products, 'color')))
    if not platform:
        filter_list.append(('商城', 'platform', get_filter_list(products, 'platform')))

    return products, filtered, filter_list


def washer_filter(request):
    products = Washer.objects.all()
    filtered = []
    filter_list = []
    products = get_products_by_search(products, request.GET.get('str'))
    color = request.GET.get('color')
    platform = request.GET.get('platform')
    brand = request.GET.get('brand')
    open_method = request.GET.get('open_method')
    drain_method = request.GET.get('drain_method')
    rank = request.GET.get('rank')
    price_range = request.GET.get('price_range')

    if brand:
        products = products.filter(brand=brand)
        filtered.append(('品牌', 'brand', brand))
    if open_method:
        products = products.filter(open_method=open_method)
        filtered.append(('开门方式', 'open_method', open_method))
    if drain_method:
        products = products.filter(drain_method=drain_method)
        filtered.append(('排水方式', 'drain_method', drain_method))
    if rank:
        products = products.filter(rank=rank)
        filtered.append(('能效等级', 'rank', rank))
    if price_range:
        products = price_range_filter(products, price_range)
        filtered.append(('价格范围', 'price_range', price_range))
    if color:
        products = products.filter(color=color)
        filtered.append(('颜色', 'color', color))
    if platform:
        products = products.filter(platform=platform)
        filtered.append(('商城', 'platform', platform))

    if not brand:
        filter_list.append(('品牌', 'brand', get_filter_list(products, 'brand')))
    if not open_method:
        filter_list.append(('开门方式', 'open_method', get_filter_list(products, 'open_method')))
    if not drain_method:
        filter_list.append(('排水方式', 'drain_method', get_filter_list(products, 'drain_method')))
    if not rank:
        filter_list.append(('能效等级', 'rank', get_filter_list(products, 'rank')))
    if not price_range:
        filter_list.append(('价格范围', 'price_range', get_price_range_filter_list(products)))
    if not color:
        filter_list.append(('颜色', 'color', get_filter_list(products, 'color')))
    if not platform:
        filter_list.append(('商城', 'platform', get_filter_list(products, 'platform')))

    return products, filtered, filter_list


def get_products_by_category(request, category):
    if category == '全部':
        return product_filter(request)
    if category == '手机':
        return cellphone_filter(request)
    if category == '冰箱':
        return refrigerator_filter(request)
    if category == '笔记本':
        return computer_filter(request, Laptop)
    if category == '台式电脑':
        return computer_filter(request, Desktop)
    if category == '电视机':
        return television_filter(request)
    if category == '洗衣机':
        return washer_filter(request)
    return None, None, None


def takeFirst(elem):
    return elem[0]


def products_filter(request, category):
    if not category:
        return index(request)
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
        words = seg.cut(search_string)
        for word in words:
            search_string = word.upper()
            for product in products:
                l = len(search_string)
                if search_string in product.model.upper():
                    model = product.model
                    model_upper = model.upper()
                    num = model_upper.count(search_string)
                    last_index = -1
                    for i in range(num):
                        model_index = model_upper.index(search_string, last_index + 1)
                        last_index = model_index + 30
                        model = model[:model_index] + '<em style="color: #c00;">' + model[model_index:model_index + l] + '</em>' + model[model_index + l:]
                        model_upper = model.upper()
                    product.model = model
                if search_string in product.title.upper():
                    title = product.title
                    title_upper = title.upper()
                    num = title_upper.count(search_string)
                    last_index = -1
                    for i in range(num):
                        title_index = title_upper.index(search_string, last_index + 1)
                        last_index = title_index + 30
                        title = title[:title_index] + '<em style="color: #c00;">' + title[title_index:title_index + l] + '</em>' + title[title_index + l:]
                        title_upper = title.upper()
                    product.title = title

    return render(request, 'products_filter.html', {'products': products,
                                                    'max_page': paginator.num_pages, 'total_result': total_result,
                                                    'category': category, 'filter_list': filter_list,
                                                    'filtered': filtered if filtered else None,
                                                    'sort_list': sort_list, 'common': common,
                                                    'search_string': request.GET.get('str')})


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


def get_refrigerator_detail(product):
    return [
        [('品牌', product.brand), ('上市时间', product.date), ('颜色', product.color)],
        [('开门方式', product.open_method), ('气候类型', product.weather), ('电压/频率', product.voltFre)],
        [('能效等级', product.rank), ('冷冻能力', product.ability), ('制冷方式', product.method)],
        [('运转音dB(A)', product.dB), ('产品重量', product.weight), ('冷藏室容积', product.cold_volume)],
        [('冷冻室容积', product.ice_volume), ('外形尺寸（宽*深*高）', product.form_size), ('包装尺寸（宽*深*高）', product.case_size)],
    ]


def get_laptop_detail(product):
    return [
        [('品牌', product.brand), ('上市时间', product.date), ('颜色', product.color)],
        [('操作系统', product.os), ('核心数', product.core), ('CPU型号', product.cpu)],
        [('内存容量', product.ram), ('固态硬盘', product.ssd), ('机械硬盘', product.hdd)],
        [('显卡型号', product.graphic_card), ('重量', product.weight), ('屏幕分辨率', product.frequency)],
    ]


def get_desktop_detail(product):
    return [
        [('品牌', product.brand), ('上市时间', product.date), ('颜色', product.color)],
        [('操作系统', product.os), ('核心数', product.core), ('CPU型号', product.cpu)],
        [('内存容量', product.ram), ('固态硬盘', product.ssd), ('机械硬盘', product.hdd)],
        [('显卡型号', product.graphic_card), ('重量', product.weight)],
    ]


def get_television_detail(product):
    return [
        [('品牌', product.brand), ('上市时间', product.date), ('电视类型', product.tv_category)],
        [('屏幕尺寸', product.length), ('屏幕分辨率', product.frequency), ('光源类型', product.light)],
        [('产品颜色', product.color), ('屏幕比例', product.ratio), ('操作系统', product.os)],
        [('RAM内存（DDR）', product.ram), ('ROM存储（EMMC）', product.rom), ('整机功率（W）', product.machine_power)],
        [('待机功率（W）', product.wait_power), ('电源电压', product.volt), ('单屏尺寸（宽*高*厚）', product.size),],
        [('单屏重量（KG）', product.weight),],
    ]


def get_washer_detail(product):
    return [
        [('品牌', product.brand), ('上市时间', product.date), ('颜色', product.color)],
        [('开门方式', product.open_method), ('排水方式', product.drain_method), ('产品重量', product.weight)],
        [('洗衣容量', product.wash_volume), ('脱水容量', product.dewater_volume)],
        [('外形尺寸（宽*深*高）', product.size), ('能效等级', product.rank)],
    ]


def products_detail(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    type_name = type(product).__name__
    detail_list = []
    model = Product
    category = ''
    if type_name == 'Cellphone':
        detail_list = get_cellphone_detail(product)
        model = Cellphone
        category = '手机'
    if type_name == 'Refrigerator':
        detail_list = get_refrigerator_detail(product)
        model = Refrigerator
        category = '冰箱'
    if type_name == 'Laptop':
        detail_list = get_laptop_detail(product)
        model = Laptop
        category = '笔记本'
    if type_name == 'Desktop':
        detail_list = get_desktop_detail(product)
        model = Desktop
        category = '台式电脑'
    if type_name == 'Television':
        detail_list = get_television_detail(product)
        model = Television
        category = '电视机'
    if type_name == 'Washer':
        detail_list = get_washer_detail(product)
        model = Washer
        category = '洗衣机'
    compare_list = compare_same_model(request, model, product_id)

    return render(request, 'products_detail.html', {'product': product, 'detail_list': detail_list,
                                                    'compare_list': compare_list, 'category': category})


def compare_same_model(request, model, product_id):
    product = model.objects.filter(id=product_id).first()
    products = model.objects.filter(brand=product.brand)
    products = products.filter(Q(model__iexact=product.model))
    products = products.order_by('platform')
    return products
