import re
import sys
import requests
import lxml.html
from app.models import *
from ECommerce.settings import DATABASE_NAME
from mongoengine import *
import time
from crawler.util import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class TBEngine:
    def __init__(self):
        self.isConnected = False
        self.session = requests.Session()
        self.driver = webdriver.Chrome()
        self.cellphone_info_list = [('color', '颜色'), ('os', '操作系统'), ('cpu', 'CPU品牌'), ('model', '型号'),
                                    ('frequency', '分辨率'), ('screen_size', '屏幕尺寸')]

    def get_taobao_common(self, spider):
        product_info = dict()
        product_info['title'] = self.driver.find_element_by_class_name('tb-main-title').text
        product_info['shop_name'] = self.driver.find_element_by_class_name('shop-name-title').get_attribute('title')
        product_info['image'] = self.driver.find_element_by_id('J_ImgBooth').get_attribute('src')

        ps = self.driver.find_element_by_id('attributes').find_elements_by_tag_name('p')
        for p in ps:
            text = p.text
            if '品牌' in text:
                product_info['brand'] = text.split(':')[-1].strip()
            elif '型号' in text:
                product_info['model'] = text.split(':')[-1].strip()
        self.driver.execute_script("window.scrollTo(0, 800);")
        other_info = spider()
        time.sleep(2)
        self.driver.find_element_by_xpath('//a[@shortcut-label="查看累计评论"]').click()
        good = int(self.driver.find_element_by_xpath('//span[@data-kg-rate-stats="good"]').text[1:-1])
        neutral = int(self.driver.find_element_by_xpath('//span[@data-kg-rate-stats="neutral"]').text[1:-1])
        bad = int(self.driver.find_element_by_xpath('//span[@data-kg-rate-stats="bad"]').text[1:-1])
        total = good + neutral + bad
        score = (good * 5 + neutral * 3 + bad) / total if total else 0.0
        product_info['comment_num'] = total
        product_info['score'] = score
        return {**product_info, **other_info}

    def get_tmall_common(self, spider):
        return

    def get_common_info(self, product_id, spider):
        url = 'https://item.taobao.com/item.htm?id={}'.format(product_id)
        base_info = {'platform': '淘宝', 'url': url}
        self.driver.get(url)

        product_info = dict()
        if '淘宝' in self.driver.title:
            try:
                product_info = self.get_taobao_common(spider)
            except NoSuchElementException:
                return None
        else:
            return None
        return {**base_info, **product_info}

    @staticmethod
    def get_detail_info(root, val):
        return root.find_element_by_xpath(".//th[text()='{}']/following-sibling::td".format(val)).text

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
        return float(price_list[0])

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

    def get_max_page(self):
        text = self.driver.find_element_by_xpath('//div[@class="total"]').text
        num = re.findall(re.compile(r'(\d+)'), text)
        return int(num[0]) if num else 0

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

    def get_network_info(self, net):
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

    def cellphone_spider(self):
        info = dict()
        self.driver.find_element_by_class_name("tb-attributes-more").click()
        root = self.driver.find_element_by_class_name("tb-spu-view")
        names = root.find_elements_by_xpath(".//th")
        for name in names:
            text = name.text
            if '内存' in text:
                val = name.find_element_by_xpath("./following-sibling::td").text
                data_list = ['G', 'T']
                for i in range(len(data_list)):
                    data = re.compile('\W*(\d*)' + data_list[i]).findall(val)
                    if data:
                        info['ram'] = data[-1] + 'GB' if i == 0 else data[-1] + 'TB'
                        break
                continue
            elif '存储容量' in text:
                val = name.find_element_by_xpath("./following-sibling::td").text
                data_list = ['G', 'T']
                for i in range(len(data_list)):
                    data = re.compile('\W*(\d*)' + data_list[i]).findall(val)
                    if data:
                        info['rom'] = data[-1] + 'GB' if i == 0 else data[-1] + 'TB'
                        break
                continue
            elif '网络类型' in text:
                val = name.find_element_by_xpath("./following-sibling::td").text
                info['network_support'] = self.get_network_info(val)
                continue
            for name_text, value_text in self.cellphone_info_list:
                if value_text in text:
                    info[name_text] = name.find_element_by_xpath("./following-sibling::td").text
                    break

        self.driver.find_element_by_class_name('tb-spu-close').click()
        return info

    def crawler(self, cat):
        self.driver.get('https://s.taobao.com/search?q={}'.format(cat))
        n = self.get_max_page()
        spider = None
        model = None
        if cat == '手机':
            spider = self.cellphone_spider
            model = Cellphone
        for i in range(n):
            url = "https://s.taobao.com/search?q={}&page={}".format(cat, i+1)
            self.driver.get(url)
            elements = self.driver.find_elements_by_xpath('//a[@class="product-title"]')
            urls = [elem.get_attribute('href') for elem in elements]
            for url in urls:
                self.driver.get(url)
                m = self.get_max_page()
                for j in range(m):
                    self.driver.get(url + '&s=' + str(j*44))
                    for k in range(1, 10):
                        self.driver.execute_script("window.scrollTo(0, " + str(k * 1000) + ");")
                        time.sleep(0.5)
                    root = lxml.html.etree.HTML(self.driver.page_source)
                    elements = root.xpath('//div[@class="item g-clearfix"]')
                    ids = []
                    prices = []
                    for elem in elements:
                        id = elem.xpath('.//a[@data-nid]/@data-nid')
                        price = elem.xpath('.//div[@class="price-row"]//strong/text()')
                        if id and price:
                            ids.append(id[0])
                            prices.append(float(price[0]))
                    for k in range(len(ids)):
                        product_id = ids[k]
                        info = self.get_common_info(product_id, spider)
                        if info is None:
                            continue
                        info['price'] = prices[k]
                        self.save_to_db(info, model)

    def save_to_db(self, info, model):
        if not self.isConnected:
            connect(DATABASE_NAME)
            self.isConnected = True
        if 'title' not in info:
            return

        products = model.objects.filter(url=info['url'])
        if products.first() is None:
            product = model(**info)
            product.save()
        else:
            products.update(**info)

    def login(self):
        self.driver.get('https://login.taobao.com')
        input("Continue?")


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
    tb = TBEngine()
    tb.login()
    tb.crawler('手机')
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    sys.exit(main())
