import requests
import lxml.html
import time
from selenium import webdriver
import json
from ECommerce.settings import DATABASE_NAME
from app.models import *
from mongoengine import *
from selenium.common.exceptions import NoSuchElementException
from multiprocessing import Pool, cpu_count
import sys


class SDEngine:
    def __init__(self):
        self.is_connect = False
        self.common_info_list = ['image', 'title', 'shop_name', 'url', 'price', 'comment_num', 'score']
        self.cellphone_info_list_en = ['brand', 'model', 'date', 'os', 'cpu', 'ram', 'rom', 'height', 'width', 'thickness', 'weight', 'screen_size', 'frequency', 'color', 'network_support']
        self.cellphone_info_list_cn = ['品牌', '型号', '上市时间', '手机操作系统', 'CPU品牌', '运行内存', '机身内存', '机身长度', '机身宽度', '机身厚度', '重量', '屏幕尺寸', '屏幕分辨率', '颜色', '4G网络制式']
        self.refrigerator_info_list_en = ['brand', 'model', 'date', 'color', 'open_method', 'weather', 'voltFre', 'rank', 'ability', 'method', 'dB', 'weight', 'cold_volume', 'ice_volume', 'form_size', 'case_size']
        self.refrigerator_info_list_cn = ['品牌', '型号', '上市时间', '颜色', '开门方式', '气候类型', '电压/频率', '国家能效等级', '冷冻能力', '制冷方式', '运转音dB(A)', '产品重量', '冷藏室容积', '冷冻室容积', '外形尺寸（宽*深*高）', '包装尺寸（宽*深*高）']
        self.laptop_info_list_en = ['brand', 'model', 'date', 'color', 'os', 'core', 'cpu', 'ram', 'ssd', 'hdd', 'graphic_card', 'weight', 'frequency']
        self.laptop_info_list_cn = ['品牌', '型号', '上市时间', '颜色', '操作系统', '核心数', 'CPU型号', '内存容量', '硬盘类型', '硬盘容量', '显卡型号', '重量', '屏幕分辨率']
        self.desktop_info_list_en = ['brand', 'model', 'date', 'color', 'os', 'core', 'cpu', 'ram', 'ssd', 'hdd', 'graphic_card', 'weight']
        self.desktop_info_list_cn = ['品牌', '型号', '上市时间', '颜色', '操作系统', '核心数', 'CPU型号', '内存容量', '硬盘类型', '硬盘容量', '显卡型号', '重量']
        self.television_info_list_en = ['brand', 'model', 'tv_category', 'date', 'length', 'frequency', 'light', 'color', 'ratio', 'os', 'ram', 'rom', 'machine_power', 'wait_power', 'volt', 'size', 'weight']
        self.television_info_list_cn = ['品牌', '产品型号', '电视类型', '上市时间', '屏幕尺寸', '屏幕分辨率', '光源类型', '产品颜色', '屏幕比例', '操作系统', 'RAM内存（DDR）', 'ROM存储（EMMC）', '整机功率（W）', '待机功率（W）', '电源电压', '单屏尺寸（宽*高*厚）', '单屏重量（KG）']
        self.washer_info_list_en = ['brand', 'model', 'date', 'color', 'open_method', 'drain_method', 'weight', 'wash_volume', 'dewater_volume', 'size', 'rank']
        self.washer_info_list_cn = ['品牌', '型号', '上市时间', '颜色', '开门方式', '排水方式', '产品重量', '洗衣容量', '脱水容量', '外形尺寸（宽*深*高）', '国家能效等级']

    @staticmethod
    def get_page_num(category):
        res = requests.get("https://list.suning.com/" + category + "0" + ".html")
        etree = lxml.html.etree
        root = etree.HTML(res.text)
        return int(root.xpath(
            '//div[@id="product-wrap"]/div[@id="product-list"]/div[@id="bottom_pager"]/div[@class="search-page page-fruits clearfix"]/a[@pagenum]')[-1].attrib['pagenum'])

    def is_valid(self, m_dict):
        num = 0
        for key, value in m_dict.items():
            if value == '':
                num += 1
        if (num / (len(m_dict) - 10)) > 0.3:
            return False
        return True

    @staticmethod
    def get_id_list(page_num, category):
        driver = webdriver.Chrome()
        id_list = list()
        for page in range(page_num):
            driver.get("https://list.suning.com/" + category + str(page) + ".html")
            for i in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            ID_list = driver.find_element_by_id('product-list').find_elements_by_xpath(".//ul/li[@id]")
            for id in ID_list:
                id_list.append(id.get_attribute('id').replace('-', '/'))
        print('len =', len(id_list))
        return id_list

    def init_dict(self, m_dict, model):
        for i in self.common_info_list[:4]:
            m_dict[i] = ''
        m_dict['price'] = -1
        m_dict['comment_num'] = 0
        m_dict['score'] = 0
        if model == Cellphone:
            for i in self.cellphone_info_list_en:
                m_dict[i] = ''
            m_dict['network_support'] = {'china_mobile': False, 'china_unicom': False, 'china_telecom': False,
                                         'all_kind': False}
        elif model == Refrigerator:
            for i in self.refrigerator_info_list_en:
                m_dict[i] = ''
        elif model == Laptop:
            for i in self.laptop_info_list_en:
                m_dict[i] = ''
        elif model == Desktop:
            for i in self.desktop_info_list_en:
                m_dict[i] = ''
        elif model == Television:
            for i in self.television_info_list_en:
                m_dict[i] = ''
        elif model == Washer:
            for i in self.washer_info_list_en:
                m_dict[i] = ''
        m_dict['platform'] = '苏宁'

    def save_to_db(self, m_dict, model):
        if not self.is_connect:
            connect(DATABASE_NAME)
            self.is_connect = True
        products = model.objects.filter(url=m_dict['url'])
        if products.first() is None:
            product = model(**m_dict)
            product.save()
            with open(model.__name__ + '.json', 'a', encoding='utf-8') as json_file:
                json_file.write(json.dumps(m_dict) + ',\n')
        else:
            products.update(**m_dict)

    @staticmethod
    def get_common_info(driver, m_dict):
        infoMain = driver.find_element_by_class_name('proinfo-title')
        m_dict['image'] = driver.find_element_by_id('bigImg').find_element_by_xpath('.//img').get_attribute('src')
        m_dict['title'] = infoMain.find_element_by_xpath(".//h1[@id='itemDisplayName']").text.replace('自营', '').replace('\n', '')
        m_dict['price'] = float(driver.find_element_by_class_name('mainprice').text.replace('¥', ''))
        try:
            m_dict['shop_name'] = driver.find_element_by_class_name('header-shop-inline').find_element_by_xpath(
                './/a').get_attribute('innerHTML')
        except:
            m_dict['shop_name'] = '苏宁自营'
        #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #time.sleep(5)
        driver.find_element_by_xpath('//li[@id="productCommTitle"]/a').click()
        #time.sleep(5)
        driver.implicitly_wait(5)
        comment = driver.find_element_by_css_selector("[class='rv-place-item clearfix']")
        score = 5 * int(
            comment.find_element_by_xpath(".//li[@data-type='good']").get_attribute('data-num')) + 3 * int(
            comment.find_element_by_xpath(".//li[@data-type='normal']").get_attribute('data-num')) + int(
            comment.find_element_by_xpath(".//li[@data-type='bad']").get_attribute('data-num'))
        m_dict['comment_num'] = int(
            comment.find_element_by_xpath(".//li[@data-type='total']").get_attribute('data-num'))
        m_dict['score'] = score / m_dict['comment_num']
        return

    def detail_info_crawler(self, driver, m_dict, info_list_en, info_list_cn):
        disk_type = None
        disk_size = None
        driver.find_element_by_xpath('//li[@id="productParTitle"]/a').click()
        items = driver.find_elements_by_xpath("//tr[@parametercode]")
        for item in items:
            try:
                name = item.find_element_by_xpath('.//td[@class="name"]/div/span').get_attribute('innerHTML')
            except NoSuchElementException:
                continue
            try:
                index = info_list_cn.index(name)
            except ValueError:
                continue
            val = item.find_element_by_xpath('.//td[@class="val"]')
            if name == '品牌':
                try:
                    m_dict['brand'] = val.find_element_by_xpath('.//a').get_attribute('innerHTML')
                except NoSuchElementException:
                    m_dict['brand'] = val.get_attribute('innerHTML')
            elif name == '上市时间':
                date = val.get_attribute('innerHTML')
                if '日' in date:
                    date = date.replace('年', '.').replace('月', '.').replace('日', '')
                elif '月' in date:
                    date = date.replace('年', '.').replace('月', '')
                else:
                    date = date.replace('年', '')
                if '-' in date:
                    date = date.replace('-', '.', 3)
                num = date.count('.')
                if num == 2:
                    index = date.index('.', date.index('.')+1)
                    date = date[:index]
                    index = date.index('.')
                    if len(date) - index < 3:
                        date = date[:index + 1] + '0' + date[index + 1:]
                elif num == 1:
                    index = date.index('.')
                    if len(date) - index < 3:
                        date = date[:index + 1] + '0' + date[index + 1:]
                m_dict['date'] = date
            elif name == '4G网络制式':
                m_dict['network_support'] = self.get_network_info(val.get_attribute('innerHTML'))
            elif name == '硬盘类型':
                disk_type = val.get_attribute('innerHTML')
            elif name == '硬盘容量':
                disk_size = val.get_attribute('innerHTML')
            else:
                m_dict[info_list_en[index]] = val.get_attribute('innerHTML')
        if disk_type and disk_size:
            if disk_type == '机械硬盘':
                m_dict['hdd'] = disk_size
            elif disk_type == '固态硬盘':
                m_dict['ssd'] = disk_size
            elif disk_type == '混合硬盘':
                size = disk_size.split('+')
                m_dict['hdd'] = size[0]
                m_dict['ssd'] = size[1]

    def crawling(self, category):
        if category == '0-20002-':
            info_list_en = self.cellphone_info_list_en
            info_list_cn = self.cellphone_info_list_cn
            model = Cellphone
        elif category == '0-244005-':
            info_list_en = self.refrigerator_info_list_en
            info_list_cn = self.refrigerator_info_list_cn
            model = Refrigerator
        elif category == '0-258004-':
            info_list_en = self.laptop_info_list_en
            info_list_cn = self.laptop_info_list_cn
            model = Laptop
        elif category == '0-258009-':
            info_list_en = self.desktop_info_list_en
            info_list_cn = self.desktop_info_list_cn
            model = Desktop
        elif category == '0-293006-':
            info_list_en = self.television_info_list_en
            info_list_cn = self.television_info_list_cn
            model = Television
        elif category == '0-244006-':
            info_list_en = self.washer_info_list_en
            info_list_cn = self.washer_info_list_cn
            model = Washer
        else:
            return
        page_num = self.get_page_num(category)
        id_list = self.get_id_list(page_num, category)
        info = dict()
        driver = webdriver.Chrome()
        for id in id_list:
            self.init_dict(info, model)
            url = "https://product.suning.com/" + id + ".html"
            info['url'] = url
            driver.get(url)
            try:
                self.get_common_info(driver, info)
                self.detail_info_crawler(driver, info, info_list_en, info_list_cn)
            except Exception as e:
                print('exception')
                continue
            if self.is_valid(info):
                print('save')
                self.save_to_db(info, model)
            else:
                print('no')

    @staticmethod
    def get_network_info(net):
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

    def run(self):
        print('SUNING start')
        self.crawling('0-20002-')    #cellphone
        self.crawling('0-244005-')   #refrigerator
        self.crawling('0-258004-')   #laptop
        self.crawling('0-258009-')   #desktop
        self.crawling('0-293006-')   #television
        self.crawling('0-244006-')  # washer
        print('SUNING end')


def main():
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    sd = SDEngine()
    sd.crawling('0-20002-')    #cellphone
    sd.crawling('0-244005-')   #refrigerator
    sd.crawling('0-258004-')   #laptop
    sd.crawling('0-258009-')   #desktop
    sd.crawling('0-293006-')   #television
    sd.crawling('0-244006-')   #washer
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


if __name__ == '__main__':
    sys.exit(main())