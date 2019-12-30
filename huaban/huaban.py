import hashlib
import os
import re
import time
import logging
import urllib.request
from lxml import etree
from selenium import webdriver
from BaiduFaceIdentify import BaiduFaceIdentify


class HuabanDownloader():
    # 构造函数，实例化bfi、browser、pic_download_count
    def __init__(self):
        # 百度人脸检测实例
        self.bfi = BaiduFaceIdentify()
        # 用于打开首页、登录花瓣并五次下拉滚动条到底部的浏览器
        # 在调试时建议使用正常呈现界面的浏览器模式，但在程序发布时建议使用无头模式
        # 这样可以加快速度、减小资源消耗及防止误关浏览器导致程序中止
        # 无头模式和普通模式在功能和使用上毫无区别，只是在实例化时加入以下--headless和--disable-gpu两个参数
        self.browser_options = webdriver.FirefoxOptions()
        self.browser_options.add_argument('--headless')
        self.browser_options.add_argument('--disable-gpu')
        self.browser = webdriver.Firefox(firefox_options=self.browser_options)
        # 设置浏览器页面加载超时时间，这里设置15秒
        self.browser.set_page_load_timeout(15)
        # 类成员变量，用于保存共下载的图片张数
        self.pic_download_count = 0


    # 此函数用于登录花瓣网
    def login_in(self, login_page_url):
        try:
            # 使用浏览器打开花瓣网，以准备登录
            self.browser.get(login_page_url)
        except Exception:
            # 如果加载超时，直接中止加载未完成内容运行后续代码
            self.browser.execute_script('window.stop()')
        time.sleep(1)
        # 找到登录按钮并点击，唤出登录对话框
        self.browser.find_element_by_xpath('//a[@class="login bounce btn wbtn"]').click()
        # 找到用户名输入框，填写用户名（我贴上来时乱改的，运行时改成自己花瓣网的用户名）
        self.browser.find_element_by_name('email').send_keys('who602@qq.com')
        # 找到密码输入框，填写密码（我贴上来时乱改的，运行时改成自己的密码）
        self.browser.find_element_by_name('password').send_keys('lshjztzy6')
        # 找到登录按钮并点击登录
        self.browser.find_element_by_css_selector('a.btn:nth-child(4)').click()
        time.sleep(2)

    # 此函数用于打开main_page，下拉五次滚动条，然后提取页面所有目标a标签的href
    def open_main_page(self,main_page_url):
        try:
            # 登录后会自动重定向到个人主页，我们手动重定向到main_page
            self.browser.get(main_page_url)
        except Exception:
            # 如果加载超时，直接中止加载未完成内容运行后续代码
            self.browser.execute_script('window.stop()')
        # for模拟用户4次将浏览器滚动条拉到了底部，由于打开时直接展示一个版面，所以下拉4次后最终是五个版面
        # 这设置在我电脑跑了一个多小时下载五百多张图片，到后边已有一些重复率
        for i in range(1,5):
            logging.warning('开始第'+ str(i) +'次下拉滚动条')
            # 浏览器执行js将滚动条拉到底部
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(2)

        # 获取当前浏览器界面的html源代码
        content = self.browser.page_source
        # 使用lxml解析内容构建选择器
        sel = etree.HTML(content)
        # 提取目标a标签的href属性值
        image_view_page_urls = sel.xpath('//div[@id="waterfall"]//a[@class="img x layer-view loaded"]/@href')
        # 关闭浏览器，实际使用发现浏览器5秒以上没操作后面就没用了，所以不关留着后面也用不了
        self.browser.quit()
        # 遍历浏览页面a标签的href属性值，也就是view_page
        for image_view_page_url in image_view_page_urls:
            # 匹配“pins/”+6位以上数值的url才是我们的目标view_page
            if re.search('pins/\d{6,}',image_view_page_url):
                logging.warning('view_page url格式匹配，即将进入：' + image_view_page_url)
                image_view_page_url_temp = 'http://huaban.com' + image_view_page_url
                self.get_img_url_from_view_page(image_view_page_url_temp)
            else:
                logging.warning('view_page url格式不匹配，将不进入：'+ image_view_page_url)


    # 此函数负责从view_page中抽取图片src，并将本次view_page的所有src传到百度识别接口，获取检测结果
    def get_img_url_from_view_page(self, image_view_page_url):
        # 每次都实例化一个浏览器来打开传来的url
        browser_view_page_options = webdriver.FirefoxOptions()
        browser_view_page_options.add_argument('--headless')
        browser_view_page_options.add_argument('--disable-gpu')
        browser_view_page = webdriver.Firefox(firefox_options=browser_view_page_options)
        browser_view_page.set_page_load_timeout(5)
        try:
            # 打开url
            browser_view_page.get(image_view_page_url)
        except Exception:
            # 如果到时间还没加载完成那就终止还没完成的加载，直接进行后续步骤
            browser_view_page.execute_script('window.stop()')
        # 获取当前浏览器界面的html源代码
        content = browser_view_page.page_source
        # 使用lxml解析内容构建选择器
        sel = etree.HTML(content)
        # 从view_page中抽取图片src
        img_urls = sel.xpath('//div[@id="board_pins_waterfall"]//img/@src')
        # 关闭浏览器，实际使用发现浏览器5秒以上没操作后面就没用了，所以不关留着后面也用不了
        browser_view_page.quit()
        # 遍历当前view_page抽取到的图片src
        for img_url in img_urls:
            # 排除gif及确保图片不是网站相对图径
            if 'gif' not in img_url and 'aicdn.com' in img_url:
                logging.warning('\r\nimg_url格式匹配，即将调用百度识别：http:' + img_url)
                img_url_tmp = 'http:' + img_url[:img_url.find('_')]
                try:
                    # 调用百度识别接口进行识别，当然这个接口是我们自己封装的BaiduFaceIdentify类
                    beauty_value = self.bfi.parse_face_pic(img_url_tmp)
                except Exception:
                    logging.error('百度识别遇到了一个错误：' + img_url_tmp)
                    continue
                # 对返回的颜值进行判断，以决定如何处理图片
                if beauty_value > 50.0:
                    logging.warning('颜值' + str(beauty_value) +'达标，准备确认图片是否已存在：' + img_url_tmp)
                    self.save_image(img_url_tmp, beauty_value)
                elif beauty_value == 1.0:
                    logging.warning('不是妹子，将不保存该图片：' + img_url_tmp)
                elif beauty_value == 0.0:
                    logging.warning('没有人脸，将不保存该图片：' + img_url_tmp)
                else:
                    logging.warning('颜值' + str(beauty_value) +'不达标，将不保存该图片：' + img_url_tmp)
            else:
                logging.warning('\r\nimg_url格式不匹配，将不调用百度识别：http' + img_url)


    # 此函数用于将颜值达标的图片保存到当前路径的pic目录下
    def save_image(self, img_url,beauty_value):
        # 图片名称使用“颜值”-“下载日期”-“url的md5值”形式
        image_name = str(beauty_value) + '-' + time.strftime("%Y%m%d", time.localtime()) + '-' + hashlib.md5(img_url.encode()).hexdigest()+'.jpg'
        # 判断pic目录是否存在，不存在则先创建
        if not os.path.exists('pic'):
            logging.warning('pic目录尚不存在，即将创建')
            os.mkdir('pic')
        # 判断图片是否之前已保存过
        if not os.path.isfile('pic\\' + image_name):
            logging.warning('图片尚不存在，即将保存：'+ image_name)
            # 保存图片
            urllib.request.urlretrieve(img_url, 'pic\\' + image_name)
            self.pic_download_count += 1
            logging.warning('当前已保存'+ str(self.pic_download_count) + '张图片')
        else:
            logging.warning('图片已存在，将不保存：'+ image_name)


if __name__ == '__main__':
    login_page_url = 'http://huaban.com/'
    main_page_url = 'http://huaban.com/favorite/beauty/'
    huaban_downloader = HuabanDownloader()
    huaban_downloader.login_in(login_page_url)
    huaban_downloader.open_main_page(main_page_url)