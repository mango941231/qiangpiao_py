import time
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


def main():
    options = Options()
    # os.popen(r'start chrome.exe --remote-debugging-port=9527')
    options.add_experimental_option(
        "debuggerAddress", "127.0.0.1:9527"
    )  # 通过端口号接管已打开的浏览器
    driver = webdriver.Chrome(
        service=Service(r"chromedriver.exe"),
        options=options,
    )
    wait = WebDriverWait(driver, 20)
    # driver.get('https://www.globalinterpark.com/en/product/24012940')
    driver.switch_to.frame('product_detail_area')
    driver.find_element(By.XPATH, "//*[@class='btn_Booking']/img").click()
    handles = driver.window_handles
    print(handles)
    driver.switch_to.window(handles[-1])
    time_count = 0
    while 1:
        # print(driver.current_url)
        if 'BookMain' in driver.current_url:
            driver.switch_to.frame('ifrmBookStep')
            CellPlayDate = driver.find_elements(By.ID, "CellPlayDate")
            if len(CellPlayDate) > 0:
                CellPlayDate[-1].click()
                time.sleep(1)
                driver.switch_to.default_content()
                driver.find_element(By.ID, "LargeNextBtnImage").click()
                # divRecaptcha_v2
                time.sleep(2)
                driver.switch_to.frame('ifrmSeat')
                while 1:
                    captcha_info = driver.find_element(By.XPATH, "//*[@id='divRecaptcha_v2']").get_attribute('style')
                    if captcha_info.strip() != '':
                        break
                    time.sleep(2)
                # driver.switch_to.frame('ifrmSeat')
                driver.switch_to.frame('ifrmSeatDetail')
                zw = driver.find_elements(By.CLASS_NAME, "stySeat")
                if len(zw) == 0:
                    zw = driver.find_elements(By.CLASS_NAME, "SeatN")
                print("空座：", len(zw))
                if len(zw) > 0:
                    zw[0].click()
                    time.sleep(1)
                    driver.switch_to.default_content()
                    driver.switch_to.frame('ifrmSeat')
                    driver.find_element(By.ID, "NextStepImage").click()
                    # wait.until(EC.visibility_of_element_located((By.ID, "ifrmBookStep")))
                    time.sleep(1)
                    driver.switch_to.default_content()
                    driver.switch_to.frame('ifrmBookStep')
                    select = Select(driver.find_element(By.NAME, "SeatCount"))
                    select.select_by_index(1)
                    time.sleep(1)
                    driver.switch_to.default_content()
                    driver.find_element(By.ID, "SmallNextBtnImage").click()
                    time.sleep(1)
                    driver.switch_to.frame('ifrmBookStep')
                    driver.find_element(By.ID, "PhoneNo").clear()
                    driver.find_element(By.ID, "PhoneNo").send_keys(config['购票信息']['手机号'])
                    time.sleep(1)
                    driver.switch_to.default_content()
                    driver.find_element(By.ID, "SmallNextBtnImage").click()
                    time.sleep(2)
                    wait.until(EC.visibility_of_element_located((By.ID, "SmallNextBtnImage")))
                    driver.find_element(By.ID, "SmallNextBtnImage").click()
                    time.sleep(2)
                    driver.switch_to.frame('ifrmBookStep')
                    driver.find_element(By.ID, "CancelAgree").click()
                    driver.find_element(By.ID, "CancelAgree2").click()
                    driver.switch_to.default_content()
                    driver.find_element(By.ID, "LargeNextBtnImage").click()
                    time.sleep(5)
                    handles = driver.window_handles
                    print(handles)
                    for handle in handles:
                        driver.switch_to.window(handle)
                        print(driver.current_url)
                        if 'NewGlobalStep1' in driver.current_url:
                            driver.find_elements(By.CLASS_NAME, "custom-control-label")[1].click()
                            time.sleep(1)
                            driver.find_element(By.XPATH, "//input[@id='unioncardnoTmp']").send_keys(config['购票信息']['卡号'])
                            driver.find_element(By.ID, "btnNext").click()
                            wait.until(EC.visibility_of_element_located((By.ID, "credentialNo")))
                            driver.find_element(By.ID, "credentialNo").send_keys(config['购票信息']['身份证'])
                            driver.find_element(By.ID, "btnGetCode").click()
            else:
                print('无可选日期')
        else:
            time_count +=1
            print(f"加载中。。。{time_count}")
            time.sleep(1)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('配置文件.ini', encoding='utf-8')
    if config['购票信息']['手机号'] == '':
        print('请在配置文件中设置手机号！')
        time.sleep(20)
        exit(0)
    elif config['购票信息']['卡号'] == '':
        print('请在配置文件中设置卡号！')
        time.sleep(20)
        exit(0)
    elif config['购票信息']['身份证'] == '':
        print('请在配置文件中设置身份证号！')
        time.sleep(20)
        exit(0)
    try:
        main()
    except Exception as e:
        print(e)
        time.sleep(999)