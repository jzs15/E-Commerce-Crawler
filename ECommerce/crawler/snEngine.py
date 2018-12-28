import requests
import lxml.html
import time
from selenium import webdriver
from ECommerce.settings import DATABASE_NAME
from app.models import *
from mongoengine import *
from selenium.common.exceptions import NoSuchElementException
import traceback
from multiprocessing import Pool, cpu_count

class SDEngine:
    def __init__(self):
        self.is_connect = False
        self.common_info_list = ['image', 'title', 'price', 'comment_num', 'score', 'shop_name', 'url']
        self.cellphone_info_list = ['brand', 'model', 'date', 'os', 'cpu', 'ram', 'rom', 'height', 'width', 'thickness', 'weight', 'screen_size', 'frequency', 'color', 'network_support']

    @staticmethod
    def get_page_num(category):
        res = requests.get("https://list.suning.com/" + category + "0" + ".html")
        etree = lxml.html.etree
        root = etree.HTML(res.text)
        return int(root.xpath('//div[@id="product-wrap"]/div[@id="product-list"]/div[@id="bottom_pager"]/div[@class="search-page page-fruits clearfix"]/a[@pagenum]')[-1].attrib['pagenum'])

    @staticmethod
    def get_id_list(page_num, category):
        driver = webdriver.Chrome()
        id_list = list()
        for page in range(page_num):
            driver.get("https://list.suning.com/" + category + str(page) + ".html")
            for i in range(10):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            ID_list = driver.find_element_by_id('product-list').find_elements_by_xpath(".//ul/li[@id]")
            for id in ID_list:
                id_list.append(id.get_attribute('id').replace('-', '/'))
        return id_list


    def init_dict(self, m_dict):
        for i in self.common_info_list:
            m_dict[i] = 'None'
        for i in self.cellphone_info_list:
            m_dict[i] = 'None'
        m_dict['platform'] = '苏宁'
        m_dict['network_support'] = {'china_mobile': False, 'china_unicom': False, 'china_telecom': False, 'all_kind': False}


    def save_to_db(self, m_dict, model):
        if not self.is_connect:
            connect(DATABASE_NAME)
            self.is_connect = True
        products = model.objects.filter(url=m_dict['url'])
        if products.first() is None:
            product = model(**m_dict)
            product.save()
        else:
            products.update(**m_dict)


    @staticmethod
    def get_common_info(driver, m_dict):
        infoMain = driver.find_element_by_class_name('proinfo-title')
        m_dict['image'] = driver.find_element_by_id('bigImg').find_element_by_xpath('.//img').get_attribute('src')
        m_dict['title'] = infoMain.find_element_by_xpath(".//h1[@id='itemDisplayName']").text.replace('自营', '').replace('\n', '')
        m_dict['price'] = float(driver.find_element_by_class_name('mainprice').text.replace('¥', ''))
        try:
            m_dict['shop_name'] = driver.find_element_by_class_name('header-shop-inline').find_element_by_xpath('.//a').get_attribute('innerHTML')
        except:
            m_dict['shop_name'] = 'None'

        driver.find_element_by_xpath('//li[@id="productCommTitle"]/a').click()
        driver.implicitly_wait(3)
        comment = driver.find_element_by_css_selector("[class='rv-place-item clearfix']")
        score = 5 * int(
            comment.find_element_by_xpath(".//li[@data-type='good']").get_attribute('data-num')) + 3 * int(
            comment.find_element_by_xpath(".//li[@data-type='normal']").get_attribute('data-num')) + int(
            comment.find_element_by_xpath(".//li[@data-type='bad']").get_attribute('data-num'))
        m_dict['comment_num'] = int(comment.find_element_by_xpath(".//li[@data-type='total']").get_attribute('data-num'))
        m_dict['score'] = score / m_dict['comment_num']
        return


    def cellphone_crawler(self, driver, m_dict):
        driver.find_element_by_xpath('//li[@id="productParTitle"]/a').click()
        items = driver.find_elements_by_xpath("//tr[@parametercode]")
        for item in items:
            try:
                name = item.find_element_by_xpath('.//td[@class="name"]/div/span').get_attribute('innerHTML')
            except NoSuchElementException:
                continue
            val = item.find_element_by_xpath('.//td[@class="val"]')
            if name == '品牌':
                m_dict['brand'] = val.find_element_by_xpath('.//a').get_attribute('innerHTML')
            elif name == '型号':
                m_dict['model'] = val.get_attribute('innerHTML')
            elif name == '上市时间':
                date = val.get_attribute('innerHTML')
                if '月' in date:
                    date = date.replace('年', '.').replace('月', '')
                else:
                    date = date.replace('年', '')
                if '.' in date:
                    index = date.find('.')
                    date = date[:index + 1] + '0' + date[index + 1:]
                m_dict['date'] = date
            elif name == '手机操作系统':
                m_dict['os'] = val.get_attribute('innerHTML')
            elif name == 'CPU品牌':
                m_dict['cpu'] = val.get_attribute('innerHTML')
            elif name == '运行内存':
                m_dict['ram'] = val.get_attribute('innerHTML')
            elif name == '机身内存':
                m_dict['rom'] = val.get_attribute('innerHTML')
            elif name == '机身长度':
                m_dict['height'] = val.get_attribute('innerHTML')
            elif name == '机身宽度':
                m_dict['width'] = val.get_attribute('innerHTML')
            elif name == '机身厚度':
                m_dict['thickness'] = val.get_attribute('innerHTML')
            elif name == '重量':
                m_dict['weight'] = val.get_attribute('innerHTML')
            elif name == '屏幕尺寸':
                m_dict['screen_size'] = val.get_attribute('innerHTML')
            elif name == '屏幕分辨率':
                m_dict['frequency'] = val.get_attribute('innerHTML')
            elif name == '颜色':
                m_dict['color'] = val.get_attribute('innerHTML')
            elif name == '4G网络制式':
                network_support = val.get_attribute('innerHTML')
                network_support = network_support if network_support else ''
                m_dict['network_support'] = self.get_network_info(network_support)


    def crawling(self, category):
        page_num = 1 #self.get_page_num(category)
        crawler = None
        model = None
        if category == '0-20002-':
            crawler = self.cellphone_crawler
            model = Cellphone
        id_list = self.get_id_list(page_num, category)
        info = dict()
        driver = webdriver.Chrome()
        num = 1
        for id in id_list:
            self.init_dict(info)
            url = "https://product.suning.com/" + id + ".html"
            info['url'] = url

            print(num)
            print(url)
            num += 1

            driver.get(url)
            try:
                self.get_common_info(driver, info)
                crawler(driver, info)
            except Exception as e:
                traceback.print_tb(e)
                continue
            self.save_to_db(info, model)
        '''
        pool = Pool()
        ITERATION_COUNT = cpu_count() - 1
        count_per_iteration = len(id_list) / float(ITERATION_COUNT)
        for i in range(ITERATION_COUNT):
            list_start = int(count_per_iteration * i)
            list_end = int(count_per_iteration * (i+1))
            pool.apply_async(self.info_crawling, id_list[])
        '''


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


def main():
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    sd = SDEngine()
    sd.crawling('0-20002-')
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )


main()