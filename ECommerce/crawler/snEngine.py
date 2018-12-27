import requests
import lxml.html
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import urllib.request
from ECommerce.settings import DATABASE_NAME
from app.models import *
from mongoengine import *

class SDEngine:
    def __init__(self):
        self.is_connect = False
        self.suning_url = "https://list.suning.com/"
        self.category = "0-20002-"
        self.html = ".html"
        self.product_page = "https://product.suning.com/"
        self.id_list = list()
        self.info_list = ['image', 'title', 'price', 'comment_num', 'score', 'company', 'model', 'date', 'os', 'cpu', 'ram', 'height', 'width', 'thickness', 'weight', 'screen_size', 'frequency', 'color', 'network_support', 'url']


    def get_page_num(self):
        res = requests.get(self.suning_url + self.category + "0" + self.html)
        etree = lxml.html.etree
        root = etree.HTML(res.text)
        self.page_num = int(root.xpath('//div[@id="product-wrap"]/div[@id="product-list"]/div[@id="bottom_pager"]/div[@class="search-page page-fruits clearfix"]/a[@pagenum]')[-1].attrib['pagenum'])


    def get_id_list(self):
        driver = webdriver.Chrome()
        for page in range(self.page_num):
            driver.get(self.suning_url + self.category + str(page) + self.html)
            for i in range(7):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
            list = driver.find_element_by_id('product-list').find_elements_by_xpath(".//ul/li[@id]")
            for id in list:
                self.id_list.append(id.get_attribute('id').replace('-', '/'))


    def init_dict(self, m_dict):
        for i in self.info_list:
            m_dict[i] = 'None'
        m_dict['platform'] = '苏宁'


    def save_to_db(self, m_dict):
        if not self.is_connect:
            connect(DATABASE_NAME)
            self.is_connect = True
        product = Product(**m_dict)
        product.save()
        return


    def get_information(self):
        self.init_dict(m_dict)
        driver = webdriver.Chrome()
        num = 1
        for id in self.id_list:
            print(num)
            num += 1
            print(self.product_page + id + self.html)
            m_dict['url'] = self.product_page + id + self.html
            driver.get(self.product_page + id + self.html)
            for i in range(10):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
            if len(driver.find_elements_by_css_selector("[class='rv-place-item clearfix']")) == 0:
                driver.refresh()
                time.sleep(5)
            infoMain = driver.find_element_by_class_name('proinfo-title')
            m_dict['image'] = driver.find_element_by_id('bigImg').find_element_by_xpath('.//img').get_attribute('src')
            m_dict['title'] = infoMain.find_element_by_xpath(".//h1[@id='itemDisplayName']").text
            m_dict['price'] = float(driver.find_element_by_class_name('mainprice').text.replace('¥', ''))

            comment = driver.find_element_by_css_selector("[class='rv-place-item clearfix']")
            score = 5 * int(
                comment.find_element_by_xpath(".//li[@data-type='good']").get_attribute('data-num')) + 3 * int(
                comment.find_element_by_xpath(".//li[@data-type='normal']").get_attribute('data-num')) + int(
                comment.find_element_by_xpath(".//li[@data-type='bad']").get_attribute('data-num'))
            m_dict['comment_num'] = int(comment.find_element_by_xpath(".//li[@data-type='total']").get_attribute('data-num'))
            m_dict['score'] = score / m_dict['comment_num']

            try:
                item = driver.find_element_by_id("itemParameter").find_elements_by_xpath(".//tr/td[@class='val']")
                para_name = driver.find_element_by_id("itemParameter").find_elements_by_xpath(".//tr/td[@class='name']")
                for n, i in zip(para_name, range(len(para_name))):
                    name = n.find_element_by_xpath('.//div/span').get_attribute('innerHTML')
                    if name == '品牌':
                        m_dict['company'] = item[i].find_element_by_xpath('.//a').get_attribute('innerHTML')
                    elif name == '型号':
                        m_dict['model'] = item[i].get_attribute('innerHTML')
                    elif name == '上市时间':
                        date = item[i].get_attribute('innerHTML')
                        if '月' in date:
                            date = date.replace('年', '.').replace('月', '')
                        else:
                            date = date.replace('年', '')
                        if '.' in date:
                            index = date.find('.')
                            date = date[:index+1] + '0' + date[index+1:]
                        m_dict['date'] = date
                    elif name == '手机操作系统':
                        m_dict['os'] = item[i].get_attribute('innerHTML')
                    elif name == 'CPU品牌':
                        m_dict['cpu'] = item[i].get_attribute('innerHTML')
                    elif name == '运行内存':
                        m_dict['ram'] = item[i].get_attribute('innerHTML')
                    elif name == '机身长度':
                        m_dict['height'] = item[i].get_attribute('innerHTML')
                    elif name == '机身宽度':
                        m_dict['width'] = item[i].get_attribute('innerHTML')
                    elif name == '机身厚度':
                        m_dict['thickness'] = item[i].get_attribute('innerHTML')
                    elif name == '重量':
                        m_dict['weight'] = item[i].get_attribute('innerHTML')
                    elif name == '屏幕尺寸':
                        m_dict['screen_size'] = item[i].get_attribute('innerHTML')
                    elif name == '屏幕分辨率':
                        m_dict['frequency'] = item[i].get_attribute('innerHTML')
                    elif name == '颜色':
                        m_dict['color'] = item[i].get_attribute('innerHTML')
                    elif name == '4G网络制式':
                        m_dict['network_support'] = item[i].get_attribute('innerHTML')
            except:
                continue
            self.save_to_db(m_dict)


def main():
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
    SDcrawler = SDEngine()
    SDcrawler.get_page_num()
    SDcrawler.get_id_list()
    SDcrawler.get_information()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )


m_dict = dict()
main()