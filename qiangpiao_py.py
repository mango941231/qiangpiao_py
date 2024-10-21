import time
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from recaptcha_img import get_location
import schedule


class Interpark:

    def __init__(self):
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
                img_url = img[0].find_element(By.XPATH, ".//img").get_attribute('src')
                print(img_url)
                location = get_location(img_url, tag_name)
                for l in location:
                    img[l].click()
                self.driver.find_element(By.ID, "recaptcha-verify-button").click()
            time.sleep(2)

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
                self.pass_captcha()
                self.driver.switch_to.frame('ifrmSeatDetail')
        return vs

    def choose_seat(self):
        """
        选座
        :return:
        """
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame('ifrmSeat')
        self.driver.switch_to.frame('ifrmSeatDetail')
        # 判断是否要选区域
        if len(self.driver.find_elements(By.ID, 'MainMap')) > 0:
            # 不选区域情况
            vs = self.get_vacant_seat()
        else:
            vs = self.select_area()
        if len(vs) > 0:
            vs[0].click()
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame('ifrmSeat')
            self.driver.find_element(By.ID, "NextStepImage").click()
            time.sleep(1)
            return True
        else:
            self.click_previous()
            return False

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