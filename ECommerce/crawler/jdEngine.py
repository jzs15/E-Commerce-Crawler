import re
import sys
import requests
import lxml.html
from app.models import *
from ECommerce.settings import DATABASE_NAME
from mongoengine import *
import time
from crawler.util import *
import json


class JDEngine:
    def __init__(self):
        self.isConnected = False
        self.session = requests.Session()

        self.cellphone_info_list = [('color', '机身颜色'), ('os', '操作系统'), ('cpu', 'CPU品牌'), ('ram', 'RAM'),
                                    ('rom', 'ROM'), ('frequency', '分辨率'), ('screen_size', '主屏幕尺寸（英寸）')]
        self.refrigerator_info_list = [('color', '颜色'), ('open_method', '开门方式'), ('weather', '气候类型'),
                                       ('voltFre', '电压/频率'), ('rank', '能效等级'), ('ability', '冷冻能力(kg/24h)'),
                                       ('method', '制冷方式'), ('dB', '运转音dB(A)'), ('weight', '产品重量（kg）'),
                                       ('cold_volume', '冷藏室(升)'), ('ice_volume', '冷冻室(升)'),
                                       ('form_size', '产品尺寸（深x宽x高）mm'), ('case_size', '包装尺寸（深x宽x高）mm')]
        self.laptop_info_list = [('color', '颜色'), ('os', '操作系统'),
                                 ('cpu', 'CPU型号'), ('ram', '内存容量'),
                                 ('graphic_card', '显示芯片'), ('weight', '净重'),
                                 ('frequency', '物理分辨率')]
        self.desktop_info_list = [('color', '颜色'), ('os', '操作系统'), ('cpu', 'CPU型号'),
                                  ('graphic_card', '显示芯片'), ('weight', '重量')]

    def get_common_info(self, product_id, spider):
        url = "https://item.jd.com/{}.html".format(product_id)
        res = get_request(url, self.session)
        if res is None:
            return
        root = lxml.html.etree.HTML(res.text)
        product_info = {'platform': '京东'}

        shop_name = root.xpath("//div[@class='name']/a/@title|//div[@class='shopName']/strong/span/a/text()")
        product_info['shop_name'] = str(shop_name[0]) if shop_name else '京东自营'

        image_url = root.xpath('//img[@id="spec-img"]/@data-origin')
        product_info['image'] = str(image_url[0]) if image_url else ''
        brand = root.xpath("//ul[@id='parameter-brand']/li/@title")
        brand = str(brand[0]) if brand else None
        if not brand:
            brand = self.get_detail_info(root, "品牌")
        product_info['brand'] = brand

        model = root.xpath('//ul[@class="parameter2 p-parameter-list"]/li[1]/@title|//'
                           'ul[@class="parameter2"]/li[1]/@title')
        model = str(model[0]) if model else ''
        if not model:
            model = self.get_detail_info(root, "型号")

        title = root.xpath("//div[@class='sku-name']/text()")
        product_info['title'] = self.get_title(title) if title else model
        product_info['model'] = model
        product_info['date'] = self.get_date(root)
        product_info['price'] = self.get_price(product_id)
        product_info['url'] = url
        evaluation = self.get_evaluation(product_id)
        other_info = spider(root)
        return {**product_info, **evaluation, **other_info}

    @staticmethod
    def get_detail_info(root, val, parent=None):
        if parent is None:
            detail = root.xpath("//dt[text()='{}']/following-sibling::*/text()".format(val))
        else:
            detail = root.xpath(
                "//h3[text()='{}']/following-sibling::*//dt[text()='{}']/following-sibling::*/text()".format(parent,
                                                                                                             val))
        return str(detail[-1]) if detail else ''

    @staticmethod
    def get_title(title):
        for t in title:
            if len(t.strip()) != 0:
                return t.strip()

    def get_price(self, product_id):
        reg = r'"p":"(.*?)"'
        url = 'https://p.3.cn/prices/mgets?skuIds=J_{}'.format(product_id)
        req = get_request(url, self.session)
        page = req.text
        price_list = re.findall(re.compile(reg), page)
        return float(price_list[0]) if price_list else -1.0

    def get_evaluation(self, product_id):
        evaluation = {}
        url = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv4403&' \
              'productId={}&score=3&sortType=5&page=04&pageSize=1&isShadowSku=0&rid=0&fold=1'.format(product_id)
        page = ''
        while len(page) == 0:
            req = get_request(url, self.session)
            while req.status_code != 200:
                req = get_request(url, self.session)
            page = req.text
        good = re.findall(re.compile(r'"goodCount":(.[0-9]*)'), page)
        good = int(good[0]) if good else 0
        general = re.findall(re.compile(r'"generalCount":(.[0-9]*)'), page)
        general = int(general[0]) if general else 0
        poor = re.findall(re.compile(r'"poorCount":(.[0-9]*)'), page)
        poor = int(poor[0]) if poor else 0
        total = good + general + poor
        evaluation['comment_num'] = total
        evaluation['score'] = (good * 5 + general * 3 + poor) / total if total else 0
        return evaluation

    def get_max_page(self, cat):
        url = "https://list.jd.com/list.html?cat={}".format(cat)
        res = get_request(url, self.session)
        if res is None:
            return 0
        res.encoding = 'utf-8'
        root = lxml.html.etree.HTML(res.text)
        num = root.xpath('//span[@class="p-skip"]/em/b/text()')
        return int(num[0])

    def get_date(self, root):
        year = self.get_detail_info(root, '上市年份')
        month = self.get_detail_info(root, '上市月份')
        date = ''
        if year:
            year = str(year.replace('年', ''))
            if year.isnumeric() and month:
                date = year
                month = month.replace('月', '')
                if month.isnumeric():
                    date += '.{:02d}'.format(int(month))
        return date

    def get_network_info(self, root):
        net = self.get_detail_info(root, '4G网络')
        if net:
            china_mobile = net.find("移动") >= 0
            china_unicom = net.find("联通") >= 0
            china_telecom = net.find("电信") >= 0
            all_kind = (china_mobile and china_unicom and china_telecom) or net.find("全网通") >= 0
        else:
            china_mobile = False
            china_unicom = False
            china_telecom = False
            all_kind = False
        return {'china_mobile': china_mobile, 'china_unicom': china_unicom, 'china_telecom': china_telecom,
                'all_kind': all_kind}

    def get_disk_info(self, root, val):
        disk = self.get_detail_info(root, val)
        if disk:
            temp = disk.split()
            for t in temp:
                if t.replace('GB', '').isnumeric() or t.replace('TB', '').isnumeric():
                    return t
        return ''

    def get_core(self, root):
        core = self.get_detail_info(root, '核心')
        core = self.get_detail_info(root, '核心数') if not core else core
        if core.isnumeric():
            return core
        ab = re.compile('(\d+)核').findall(core)
        if ab:
            return ab[0]
        cn_list = ['零', '一', '双', '三', '四', '五', '六', '七', '八', '九', '十']
        cn = re.compile('([\u4e00-\u9fa5]+)核').findall(core)
        if cn:
            return str(cn_list.index(cn[0]))
        return ''

    def cellphone_spider(self, root):
        info = dict()
        for name, value in self.cellphone_info_list:
            info[name] = self.get_detail_info(root, value)
        info['network_support'] = self.get_network_info(root)
        info['weight'] = remove_remark(self.get_detail_info(root, '机身重量（g）'))
        info['thickness'] = remove_remark(self.get_detail_info(root, '机身厚度（mm）'))
        info['height'] = remove_remark(self.get_detail_info(root, '机身长度（mm）'))
        info['width'] = remove_remark(self.get_detail_info(root, '机身宽度（mm）'))
        return info

    def refrigerator_spider(self, root):
        info = dict()
        for name, value in self.refrigerator_info_list:
            info[name] = self.get_detail_info(root, value)
        return info

    def laptop_spider(self, root):
        info = dict()
        for name, value in self.laptop_info_list:
            info[name] = self.get_detail_info(root, value)
        info['core'] = self.get_core(root)
        info['hdd'] = self.get_disk_info(root, '硬盘容量')
        info['ssd'] = self.get_disk_info(root, '固态硬盘')
        return info

    def desktop_spider(self, root):
        info = dict()
        for name, value in self.desktop_info_list:
            info[name] = self.get_detail_info(root, value)
        info['core'] = self.get_core(root)
        info['ram'] = ''
        ram = self.get_detail_info(root, '容量', '内存')
        if ram:
            ram_list = re.compile('\W*(\d*)').findall(ram)
            ram = 0
            for r in ram_list:
                if r.isnumeric():
                    ram += int(r)
            info['ram'] = str(ram) + 'GB'

        rom = self.get_detail_info(root, '容量', '硬盘')
        info['hdd'] = ''
        info['ssd'] = ''
        if rom:
            ssd_list = ['GSSD', 'G SSD', 'GBSSD', 'GB SSD',
                        'TSSD', 'T SSD', 'TBSSD', 'TB SSD']
            for i in range(len(ssd_list)):
                ssd = re.compile('\W*(\d*)' + ssd_list[i]).findall(rom)
                if ssd:
                    info['ssd'] = ssd[-1] + 'GB' if i <= 3 else ssd[-1] + 'TB'
                    rom = rom.replace(ssd[-1] + ssd_list[i], '')
                    break
            hdd_list = ['G', 'T']
            for i in range(len(hdd_list)):
                hdd = re.compile('\W*(\d*)' + hdd_list[i]).findall(rom)
                if hdd:
                    info['hdd'] = hdd[-1] + 'GB' if i == 0 else hdd[-1] + 'TB'
                    break
        return info

    def crawler(self, cat):
        n = self.get_max_page(cat)
        spider = None
        model = None
        if cat == '9987,653,655':
            spider = self.cellphone_spider
            model = Cellphone
        elif cat == '737,794,878':
            spider = self.refrigerator_spider
            model = Refrigerator
        elif cat == '670,671,672':
            spider = self.laptop_spider
            model = Laptop
        elif cat == '670,671,673':
            spider = self.desktop_spider
            model = Desktop
        for i in range(n):
            url = "https://list.jd.com/list.html?cat={}&page=".format(cat) + str(i)
            res = get_request(url, self.session)
            if res is None:
                continue
            res.encoding = 'utf-8'
            root = lxml.html.etree.HTML(res.text)
            ids = root.xpath('//li[@class="gl-item"]//div[@class="gl-i-wrap j-sku-item"]/@data-sku')
            for product_id in ids:
                info = self.get_common_info(re.sub('\s', '', product_id), spider)
                self.save_to_db(info, model)

    def save_to_db(self, info, model):
        if not self.isConnected:
            connect(DATABASE_NAME)
            self.isConnected = True
        if not info['title']:
            return

        products = model.objects.filter(url=info['url'])
        if products.first() is None:
            product = model(**info)
            product.save()
        else:
            products.update(**info)


def get_request(url, session, times=0):
    if times >= 10:
        print("Request failed: " + url)
        return None
    try:
        header = {'User-Agent': 'Mozilla/5.0',
                  'charset': 'utf-8'}
        res = session.get(url, headers=header)
        if res.status_code != 200:
            time.sleep(3)
            res = get_request(url, session, times + 1)
    except ConnectionError:
        try:
            time.sleep(3)
            res = get_request(url, session, times + 1)
        except ConnectionError:
            print("Request failed: " + url)
            res = None
    return res


def main():
    start_time = time.time()
    jd = JDEngine()
    # jd.crawler('9987,653,655')
    # jd.crawler('737,794,878')
    # jd.crawler('670,671,672')
    jd.crawler('670,671,673')
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    sys.exit(main())
