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
        self.session = requests.Session()
        requests.adapters.DEFAULT_RETRIES = 5

    def get_common_info(self, product_id, spider):
        url = "https://www.amazon.cn/dp/{}".format(product_id)
        res = get_request(url, self.session)
        if res is None:
            return
        root = lxml.html.etree.HTML(res.text)
        product_info = {'platform': '亚马逊'}

        title = root.xpath("//span[@id='productTitle']/text()")
        product_info['title'] = self.get_title(title) if title else None

        shop_name = root.xpath("//span[@id='ddmMerchantMessage']/a/text()")
        product_info['shop_name'] = remove_remark(str(shop_name[0])) if shop_name else None

        image_url = root.xpath('//img[@id="landingImage"]/@src')
        product_info['image'] = str(image_url[0]).strip() if image_url else None

        brand = root.xpath("//a[@id='bylineInfo']/text()")
        product_info['brand'] = str(brand[0]) if brand else None

        text = root.xpath('//td[@class="label" and text()="功能用途"]/'
                          'following-sibling::*/text()')
        product_info['model'] = self.get_detail_info(root, "型号", text)
        product_info['date'] = self.get_date(root, text)
        price = root.xpath("//span[@id='priceblock_ourprice']/text()")
        if price:
            price = float(price[0].replace('￥', '').replace(',', ''))
        product_info['price'] = price
        product_info['url'] = url
        evaluation = self.get_evaluation(product_id)
        other_info = spider(root)
        return {**product_info, **evaluation, **other_info}

    @staticmethod
    def get_detail_info(root, val, text=None):
        detail = None
        if text:
            for t in text:
                reg = r'{} (.*)'.format(val)
                detail = re.findall(re.compile(reg), str(t))
                if detail:
                    detail = str(detail[-1]).strip()
                    if len(detail):
                        return detail

        if not text or not detail:
            detail = root.xpath('//td[@class="label" and text()="{}"]/'
                                'following-sibling::*/text()'.format(val))
        return str(detail[-1]) if detail else ''

    @staticmethod
    def get_title(title):
        for t in title:
            if len(t.strip()) != 0:
                return t.strip()

    def get_evaluation(self, product_id):
        evaluation = {}
        url = 'https://www.amazon.cn/product-reviews/{}'.format(product_id)
        one = self.get_eval_num(url + '?filterByStar=one_star')
        two = self.get_eval_num(url + '?filterByStar=two_star')
        three = self.get_eval_num(url + '?filterByStar=three_star')
        four = self.get_eval_num(url + '?filterByStar=four_star')
        five = self.get_eval_num(url + '?filterByStar=five_star')
        total = one + two + three + four + five
        evaluation['comment_num'] = total
        evaluation['score'] = (five * 5 + four * 4 + three * 3 + two * 2 + one) / total if total else 0
        return evaluation

    def get_eval_num(self, url):
        res = get_request(url, self.session)
        root = lxml.html.etree.HTML(res.text)
        text = root.xpath("//div[@id='cm_cr-review_list']/div/span[@class='a-size-base']/text()")
        text = text[0] if text else ''
        reg = r'共 (.*?) 条评论'
        count = re.findall(re.compile(reg), text)
        return int(count[0]) if count else 0

    def get_max_page(self, cat):
        url = "https://www.amazon.cn/s/ref=sv_cps_0?node={}".format(cat)
        res = get_request(url, self.session)
        if res is None:
            return 0
        res.encoding = 'utf-8'
        root = lxml.html.etree.HTML(res.text)
        num = root.xpath('//div[@id="pagn"]/span[@class="pagnDisabled"]/text()')
        return int(num[0])

    def get_date(self, root, text):
        year = self.get_detail_info(root, '上市年份', text)
        month = self.get_detail_info(root, '上市月份', text)
        date = ''
        if year:
            year = str(year.replace('年', ''))
            if year.isnumeric() and month:
                date = year
                month = month.replace('月', '')
                if month.isnumeric():
                    date += '.{:02d}'.format(int(month))
        else:
            date = self.get_detail_info(root, '型号年份')
        return date

    def get_network_info(self, root, val, text):
        net = self.get_detail_info(root, val, text)
        if net:
            all_kind = net.find("全网通") >= 0
            china_mobile = all_kind or net.find("移动") >= 0
            china_unicom = all_kind or net.find("联通") >= 0
            china_telecom = all_kind or net.find("电信") >= 0
            all_kind = (china_mobile and china_unicom and china_telecom)
        else:
            china_mobile = False
            china_unicom = False
            china_telecom = False
            all_kind = False
        return {'china_mobile': china_mobile, 'china_unicom': china_unicom, 'china_telecom': china_telecom,
                'all_kind': all_kind}

    def get_size_info(self, root, text):
        info = dict()
        info['weight'] = self.get_detail_info(root, '机身重量（g）', text)
        info['thickness'] = self.get_detail_info(root, '机身厚度（mm）', text)
        info['height'] = self.get_detail_info(root, '机身长度（mm）', text)
        info['width'] = self.get_detail_info(root, '机身宽度（mm）', text)
        if not info['width']:
            info['width'] = self.get_detail_info(root, '商品重量')
        if not (info['weight'] or info['thickness'] or info['height']):
            size = self.get_detail_info(root, '商品尺寸')
            size = size.split() if size else []
            if len(size) is 6:
                info['height'] = size[0] + size[5]
                info['weight'] = size[2] + size[5]
                info['thickness'] = size[4] + size[5]
        return info



    def cellphone_spider(self, root):
        info = dict()
        text = root.xpath('//td[@class="label" and text()="功能用途"]/'
                          'following-sibling::*/text()')
        text = list(text) if text else None
        info['color'] = self.get_detail_info(root, '产品颜色', text)
        info['os'] = self.get_detail_info(root, '操作系统', text)
        info['cpu'] = self.get_detail_info(root, 'CPU品牌', text)
        info['ram'] = self.get_detail_info(root, 'RAM', text)
        info['rom'] = self.get_detail_info(root, '容量', text)
        info['frequency'] = self.get_detail_info(root, '分辨率', text)
        info['screen_size'] = self.get_detail_info(root, '屏幕尺寸', text)
        info['network_support'] = self.get_network_info(root, '网络制式', text)
        size_info = self.get_size_info(root, text)
        return {**info, **size_info}

    def crawler(self, cat):
        n = self.get_max_page(cat)
        spider = None
        model = None
        if cat == '665002051':
            spider = self.cellphone_spider
            model = Cellphone
        for i in range(n):
            url = "https://www.amazon.cn/s/ref=sv_cps_0?node={}&page={}".format(cat, i)
            res = get_request(url, self.session)
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
    az = AZEngine()
    az.crawler('665002051')
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    sys.exit(main())
