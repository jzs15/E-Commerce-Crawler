import re
import sys
import requests
import lxml.html
from app.models import *
from ECommerce.settings import DATABASE_NAME
from mongoengine import *
import time
from crawler.util import *


class AZEngine:
    def __init__(self):
        self.isConnected = False
        requests.adapters.DEFAULT_RETRIES = 5

    def get_common_info(self, product_id, spider):
        url = "https://item.jd.com/{}.html".format(product_id)
        res = get_request(url)
        if res is None:
            return
        root = lxml.html.etree.HTML(res.text)
        product_info = {'platform': '亚马逊'}

        title = root.xpath("//span[@id='productTitle']/text()")
        product_info['title'] = self.get_title(title) if title else None

        shop_name = root.xpath("//span[@id='ddmMerchantMessage']/a/text()")
        product_info['shop_name'] = str(shop_name) if shop_name else None

        image_url = root.xpath('//img[@id="landingImage"]/@src')
        product_info['image'] = str(image_url[0]) if image_url else None

        brand = root.xpath("//a[@id='bylineInfo']/text()")
        product_info['brand'] = str(brand[0]) if brand else None

        product_info['model'] = self.get_detail_info(root, "型号")
        product_info['date'] = self.get_detail_info(root, "Amazon.cn上架时间")
        price = root.xpath("//span[@id='priceblock_ourprice']/text()")
        if price:
            price = float(price.replace('￥', '').replace(',', ''))
        product_info['price'] = price
        product_info['url'] = url
        evaluation = self.get_evaluation(product_id)
        other_info = spider(root)
        return {**product_info, **evaluation, **other_info}

    @staticmethod
    def get_detail_info(root, val):
        detail = root.xpath("//dt[text()='{}']/following-sibling::*/text()".format(val))
        return str(detail[-1]) if detail else None

    @staticmethod
    def get_title(title):
        for t in title:
            if len(t.strip()) != 0:
                return t.strip()

    @staticmethod
    def get_evaluation(product_id):
        evaluation = {}
        url = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv4403&' \
              'productId={}&score=3&sortType=5&page=04&pageSize=1&isShadowSku=0&rid=0&fold=1'.format(product_id)
        page = ''
        while len(page) == 0:
            req = get_request(url)
            while req.status_code != 200:
                req = get_request(url)
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

    @staticmethod
    def get_max_page(cat):
        url = "https://www.amazon.cn/s/ref=sv_cps_0?node={}".format(cat)
        res = get_request(url)
        if res is None:
            return 0
        res.encoding = 'utf-8'
        root = lxml.html.etree.HTML(res.text)
        num = root.xpath('//div[@id="pagn"]/span[@class="pagnDisabled"]/text()')
        return int(num[0])

    def get_date(self, root):
        year = self.get_detail_info(root, '型号年份')
        date = ''
        if year:
            year = str(year.replace('年', ''))
            if year.isnumeric():
                date = year
        return date

    def get_network_info(self, root):
        net = self.get_detail_info(root, '网络制式')
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

    def cellphone_spider(self, root):
        info = dict()
        info['color'] = self.get_detail_info(root, '机身颜色')
        info['os'] = self.get_detail_info(root, '操作系统')
        info['cpu'] = self.get_detail_info(root, 'CPU品牌')
        info['ram'] = self.get_detail_info(root, 'RAM')
        info['rom'] = self.get_detail_info(root, 'ROM')
        info['frequency'] = self.get_detail_info(root, '分辨率')
        info['screen_size'] = self.get_detail_info(root, '主屏幕尺寸（英寸）')
        info['network'] = self.get_network_info(root)
        info['weight'] = remove_remark(self.get_detail_info(root, '机身重量（g）'))
        info['thickness'] = remove_remark(self.get_detail_info(root, '机身厚度（mm）'))
        info['height'] = remove_remark(self.get_detail_info(root, '机身长度（mm）'))
        info['width'] = remove_remark(self.get_detail_info(root, '机身宽度（mm）'))
        return info

    def crawler(self, cat):
        n = self.get_max_page(cat)
        spider = None
        model = None
        if cat == '665002051':
            spider = self.cellphone_spider
            model = Cellphone
        for i in range(n):
            url = "https://www.amazon.cn/s/ref=sv_cps_0?node={}&page={}".format(cat, i)
            res = get_request(url)
            if res is None:
                continue
            res.encoding = 'utf-8'
            root = lxml.html.etree.HTML(res.text)
            ids = root.xpath('//div[@id="mainResults"]/ul/li/@data-asin')
            for j in range(len(ids)):
                info = self.get_common_info(re.sub('\s', '', ids[j]), spider)
                self.save_to_db(info, model)

    def save_to_db(self, info, model):
        if not self.isConnected:
            connect(DATABASE_NAME)
            self.isConnected = True

        products = model.objects.filter(url=info['url'])
        if products.first() is None:
            product = model(**info)
            product.save()
        else:
            products.update(**info)


def get_request(url, times=0):
    if times >= 10:
        return None
    try:
        session = requests.Session()
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0 '}
        session.trust_env = False
        res = session.get(url, headers=header)
        if res.status_code != 200:
            time.sleep(3)
            res = get_request(url, times + 1)
    except ConnectionError:
        try:
            time.sleep(3)
            res = get_request(url, times + 1)
        except ConnectionError:
            res = None
    return res


def main():
    start_time = time.time()
    az = AZEngine()
    az.crawler('665002051')
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    sys.exit(main())
