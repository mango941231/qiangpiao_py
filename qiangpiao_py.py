import time
import configparser
import traceback
import xml.etree.ElementTree as ET
from pyquery import PyQuery as pq
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from recaptcha_img import get_location
import schedule
import base64


class Interpark:

    def __init__(self):
        self.GoodsCode = None
        self.PlaceCode = None
        self.SessionId = None
        options = Options()
        # os.popen(r'start chrome.exe --remote-debugging-port=9527')
        options.add_experimental_option(
            "debuggerAddress", "127.0.0.1:9527"
        )  # 通过端口号接管已打开的浏览器
        self.driver = webdriver.Chrome(
            service=Service(r"chromedriver.exe"),
            options=options,
        )
        self.wait = WebDriverWait(self.driver, 30)
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'cookie': '_fbp=fb.1.1727169446426.939794601515595092; _gid=GA1.2.130519258.1729505127; cbtUser=fYNXblFucq2Tql8dnMlEsk0xLMI9nBBzoB4cqdCn0T4=; memID=vzjJMG0qlzbtIGhOAgqrPd47g9zXC6qpJDYY2CA8rtU%3D; memNo=uSH4QBAtbokjB%2Bfqm60C%2BA%3D%3D; TMem%5FNO=T33825176; TMem%5FNO%5FG=T33825176; memEmail=vzjJMG0qlzbtIGhOAgqrPd47g9zXC6qpJDYY2CA8rtU%3D; _ga_BEN1B7STVY=GS1.1.1729576779.18.1.1729577529.0.0.0; _ga=GA1.2.262842975.1727169446; _gat_UA-60117844-2=1; _ga_3840G72Z4Q=GS1.1.1729576393.20.1.1729577654.0.0.0',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i',
            'referer': 'https://gpoticket.globalinterpark.com/Global/Play/Book/BookSeat.asp?GoodsCode=24011097&PlaceCode=24000609&OnlyDeliver=68001&DBDay=12&ExpressDelyDay=0&GroupName=INSPIRE+CONCERT+SERIES+%EF%BC%832+%3A+WESTLIFE&PlaceName=%EC%9D%B8%EC%8A%A4%ED%8C%8C%EC%9D%B4%EC%96%B4+%EC%95%84%EB%A0%88%EB%82%98&TmgsOrNot=D2003&LocOfImage=&Tiki=N&KindOfGoods=01003&GlobalSportsYN=N&isSeatCntView=N&LanguageType=G2001&MemBizCode=10965&BizCode=10965&PlayDate=20241123&PlaySeq=001&SessionId=24011097_M0000000640491729577604&BizMemberCode=T33825176&BizMemberFlag=&GoodsBizCode=53986&WynsCode=&WynsGateID=&PageCV=&kindOfChannels=,C5015,C5021,C5025,C5025,C5025,C5027,Q2033,Q2034,Q2363,&InterlockingGoods=',
        }

    def login(self):
        self.driver.get('https://www.globalinterpark.com/en/login')
        user = self.driver.find_element(By.XPATH, '//input[@type="email"]')
        user.clear()
        user.send_keys(config['INFO']['Account'])
        time.sleep(2)
        password = self.driver.find_element(By.XPATH, '//input[@type="password"]')
        password.clear()
        password.send_keys(config['INFO']['Password'])
        time.sleep(2)
        while 1:
            try:
                # self.wait.until(
                #     EC.visibility_of_element_located((By.XPATH, '//div[contains(@class, "container__Container")]/button[@type="submit"]')))
                self.driver.find_element(By.XPATH, '//div[contains(@class, "container__Container")]/button[@type="submit"]').click()
                break
            except Exception as e:
                print(e)
            time.sleep(5)

    def click_buy_tickets(self):
        """
        点击某个演唱会首页的“Buy Tickets"按钮
        :return:
        """
        # self.driver.get(config["INFO"]["Showurl"])
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame('product_detail_area')
        self.driver.find_element(By.XPATH, "//*[@class='btn_Booking']/img").click()

    def switch_window(self):
        """
        选择弹出窗口
        :return:
        """
        time_count = 0
        is_end = True
        while is_end:
            handles = self.driver.window_handles
            # print(handles)
            for handle in handles:
                self.driver.switch_to.window(handle)
                # print(self.driver.current_url)
                if 'BookMain' in self.driver.current_url:
                    break
            else:
                time_count += 1
                print(f"加载中。。。{time_count}")
                time.sleep(1)
                continue
            is_end = False


    def select_date(self):
        """
        选择日期
        :return:
        """
        count = 0
        while 1:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame('ifrmBookStep')
            CellPlayDate = self.driver.find_elements(By.ID, "CellPlayDate")
            if len(CellPlayDate) > 0:
                CellPlayDate[-1].click()
                time.sleep(1)
                self.driver.switch_to.default_content()
                self.driver.find_element(By.ID, "LargeNextBtnImage").click()
                time.sleep(2)
                break
            else:
                count += 1
                print('未发现可选日期，正在刷新...', count)
                self.driver.refresh()
                time.sleep(2)

    def pass_captcha(self):
        """
        等待处理验证码结束
        :return:
        """
        while 1:
            try:
                self.driver.switch_to.default_content()
                self.driver.switch_to.frame('ifrmSeat')
                captcha_info = self.driver.find_element(By.XPATH, "//*[@id='divRecaptcha_v2']").get_attribute('style')
                if captcha_info.strip() != '':
                    break
                else:
                    try:
                        self.driver.switch_to.frame(self.driver.find_elements(By.XPATH, "//*[@title='reCAPTCHA']")[0])
                        self.driver.find_element(By.CLASS_NAME, "recaptcha-checkbox-border").click()
                    except Exception:
                        pass
                    self.driver.switch_to.default_content()
                    self.driver.switch_to.frame('ifrmSeat')
                    # for i in self.driver.find_elements(By.TAG_NAME, "iframe"):
                    #     print(i.get_attribute('outerHTML'))
                    self.driver.switch_to.frame(self.driver.find_elements(By.TAG_NAME, "iframe")[-1])
                    # time.sleep(2)
                    self.wait.until(
                        EC.visibility_of_element_located((By.XPATH, "//*[@class='rc-imageselect-desc-wrapper']/div/strong")))
                    tag_name = self.driver.find_element(By.XPATH, "//*[@class='rc-imageselect-desc-wrapper']/div/strong").text
                    img = self.driver.find_elements(By.XPATH, "//*[@class='rc-image-tile-wrapper']")
                    # img_url = img[0].find_element(By.XPATH, ".//img").get_attribute('src')
                    # print(img_url)
                    time.sleep(2)
                    yzm_img = self.driver.find_element(By.ID, 'rc-imageselect-target')
                    yzm_jt = yzm_img.screenshot_as_png
                    with open('jietu.png', 'wb') as fw:
                        fw.write(yzm_jt)
                    # img_encoded_string = base64.b64encode(yzm_jt).decode('utf-8')
                    # print(img_encoded_string)
                    location = get_location(tag_name)
                    for l in location:
                        img[l].click()
                    self.driver.find_element(By.ID, "recaptcha-verify-button").click()
                time.sleep(3)
            except Exception as e:
                print(traceback.format_exc())
                return False

    def get_vacant_seat(self):
        """
        获取空座
        :return:
        """
        vs = self.driver.find_elements(By.CLASS_NAME, "stySeat")
        if len(vs) == 0:
            vs = self.driver.find_elements(By.CLASS_NAME, "SeatN")
        print("空座数：", len(vs))
        return vs

    def click_previous(self):
        """
        点击返回页面按钮
        :return:
        """
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame('ifrmSeat')
        self.driver.find_element(By.XPATH, "//*[@class='btnWrap']/p[@class='fl_l']").click()
        time.sleep(2)
        self.driver.switch_to.default_content()

    def select_area(self):
        vs = []
        area_num = len(self.driver.find_elements(By.XPATH, '//*[@id="TmgsTable"]//map/area'))
        for qy_no in range(1, area_num + 1):
            self.wait.until(EC.visibility_of_element_located((By.XPATH, f'//*[@id="TmgsTable"]//map/area[{qy_no}]')))
            area = self.driver.find_element(By.XPATH, f'//*[@id="TmgsTable"]//map/area[{qy_no}]')
            print('区域：', area.get_attribute('onmouseover').split("'")[1])
            area.click()
            time.sleep(2)
            vs = self.get_vacant_seat()
            if len(vs) > 0:
                break
            else:
                self.click_previous()
                self.select_date()
                if self.pass_captcha() == False:
                    break
                self.driver.switch_to.frame('ifrmSeatDetail')
        return vs

    def choose_seat(self):
        """
        选座
        :return:
        """
        self.driver.switch_to.default_content()
        self.SessionId = self.driver.find_element(By.NAME, 'SessionId').get_attribute('value')
        self.GoodsCode = self.driver.find_element(By.NAME, 'GoodsCode').get_attribute('value')
        self.PlaceCode = self.driver.find_element(By.NAME, 'PlaceCode').get_attribute('value')
        print(f'GoodsCode:{self.GoodsCode}\nPlaceCode:{self.PlaceCode}\nSessionId:{self.SessionId}')
        self.driver.switch_to.frame('ifrmSeat')
        self.driver.switch_to.frame('ifrmSeatDetail')
        # 判断是否要选区域
        if len(self.driver.find_elements(By.ID, 'MainMap')) > 0:
            # 不选区域情况
            vs = self.get_vacant_seat()
        else:
            vs = self.select_area_api()
        if len(vs) > 0:
            vs[0].click()
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame('ifrmSeat')
            self.driver.find_element(By.ID, "NextStepImage").click()
            time.sleep(1)
            return True
        else:
            # self.click_previous()
            self.driver.close()
            self.click_buy_tickets()
            return False

    def select_area_api(self):
        """
        选座（通过接口）
        :return:
        """
        vs = []
        try:
            # print(self.driver.window_handles)
            # self.driver.switch_to.window(self.driver.window_handles[0])
            # self.driver.switch_to.frame('ifrmSeat')
            # self.driver.switch_to.frame('ifrmSeatDetail')
            # self.GoodsCode = '24013283'
            # self.PlaceCode = '24001154'
            # self.SessionId = '24013283_M0000001524111729665635'
            url = f'https://gpoticket.globalinterpark.com/Global/Play/Book/Lib/BookInfoXml.asp?Flag=AllBlock&GoodsCode={self.GoodsCode}&PlaceCode={self.PlaceCode}&LanguageType=G2001&MemBizCode=10965&PlaySeq=001&Tiki=N&TmgsOrNot=D2003&SessionId={self.SessionId}'
            resp = requests.get(url, headers=self.headers).text
            # print(resp)
            html = ET.fromstring(resp)
            for i in html.findall('Table'):
                area_no = i.find('SelfDefineBlock').text
                SeatGrade = i.find('SeatGrade').text
                kz_num = self.get_seat_detail(area_no)
                print(f"区域：{area_no} 空座数：{kz_num}")
                if kz_num == None:
                    break
                if kz_num > 0:
                    self.driver.find_element(By.XPATH,
                                                       f"//*[@id='TmgsTable']//map/area[contains(@onmouseout, '{area_no}')]").click()
                    time.sleep(2)
                    vs = self.get_vacant_seat()
                    return vs
        except Exception as e:
            print(traceback.format_exc())
        return vs

    def get_seat_detail(self, Block):
        try:
            # GoodsCode = '24013283'
            # PlaceCode = '24001154'
            # SessionId = '24011097_M0000000646441729663706'
            PlaySeq = '001'
            # Block = '003'
            url = f'https://gpoticket.globalinterpark.com/Global/Play/Book/BookSeatDetail.asp?GoodsCode={self.GoodsCode}&PlaceCode={self.PlaceCode}&LanguageType=G2001&MemBizCode=10965&PlaySeq={PlaySeq}&SeatGrade=&Block={Block}&TmgsOrNot=D2003&LocOfImage=&Tiki=N&UILock=Y&SessionId={self.SessionId}&BizCode=10965&GoodsBizCode=29283&GlobalSportsYN=N&SeatCheckCnt=0&InterlockingGoods='
            resp = requests.get(url, headers=self.headers, timeout=5).text
            html = pq(resp)
            kz_num = html('#Seats').length
            return kz_num
        except Exception as e:
            print(e)
            return None

    def select_ticket_num(self):
        """
        选择票数
        :return:
        """
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame('ifrmBookStep')
        select = Select(self.driver.find_element(By.NAME, "SeatCount"))
        select.select_by_index(1)
        time.sleep(1)
        self.driver.switch_to.default_content()
        self.driver.find_element(By.ID, "SmallNextBtnImage").click()
        time.sleep(1)

    def insert_info(self):
        """
        填入购票信息
        :return:
        """
        self.driver.switch_to.frame('ifrmBookStep')
        self.driver.find_element(By.ID, "PhoneNo").clear()
        self.driver.find_element(By.ID, "PhoneNo").send_keys(config['INFO']['Phone'])
        time.sleep(1)
        self.driver.switch_to.default_content()
        self.driver.find_element(By.ID, "SmallNextBtnImage").click()
        time.sleep(2)
        self.wait.until(EC.visibility_of_element_located((By.ID, "SmallNextBtnImage")))
        self.driver.find_element(By.ID, "SmallNextBtnImage").click()
        time.sleep(2)

    def choose_agree(self):
        """
        协议勾选
        :return:
        """
        self.driver.switch_to.frame('ifrmBookStep')
        self.driver.find_element(By.ID, "CancelAgree").click()
        self.driver.find_element(By.ID, "CancelAgree2").click()
        self.driver.switch_to.default_content()
        self.driver.find_element(By.ID, "LargeNextBtnImage").click()
        time.sleep(5)

    def insert_payment_info(self):
        """
        填写支付信息
        :return:
        """
        handles = self.driver.window_handles
        # print(handles)
        for handle in handles:
            self.driver.switch_to.window(handle)
            # print(self.driver.current_url)
            if 'NewGlobalStep1' in self.driver.current_url:
                self.driver.find_elements(By.CLASS_NAME, "custom-control-label")[1].click()
                time.sleep(1)
                self.driver.find_element(By.XPATH, "//input[@id='unioncardnoTmp']").send_keys(
                    config['INFO']['Bankcard'])
                self.driver.find_element(By.ID, "btnNext").click()
                self.wait.until(EC.visibility_of_element_located((By.ID, "credentialNo")))
                self.driver.find_element(By.ID, "credentialNo").send_keys(config['INFO']['Idcard'])
                # self.driver.find_element(By.ID, "btnGetCode").click()

    def run(self):
        # self.login()
        self.click_buy_tickets()
        self.switch_window()
        while 1:
            self.select_date()
            self.pass_captcha()
            is_seat = self.choose_seat()
            if is_seat:
                self.select_ticket_num()
                self.insert_info()
                self.choose_agree()
                self.insert_payment_info()
                break
            else:
                time.sleep(2)


def main():
    task = Interpark()
    task.run()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('配置文件.ini', encoding='utf-8')
    if config['INFO']['Phone'] == '':
        print('请在配置文件中设置手机号！')
        time.sleep(20)
        exit(0)
    elif config['INFO']['Bankcard'] == '':
        print('请在配置文件中设置卡号！')
        time.sleep(20)
        exit(0)
    elif config['INFO']['Idcard'] == '':
        print('请在配置文件中设置身份证号！')
        time.sleep(20)
        exit(0)
    # try:
    #     schedule.every().day.at(config['INFO']['Runtime']).do(main)
    #     while 1:
    #         schedule.run_pending()
    #         time.sleep(1)
    # except Exception as e:
    #     print(e)
    #     time.sleep(999)
    main()