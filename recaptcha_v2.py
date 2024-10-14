
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# 你的token
token = "156543ab-4c71-4b59-a531-372581bd7739"
# 任务参数
websiteKey = "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"
websiteURL = "https://www.google.com/recaptcha/api2/demo"
task_type = "ReCaptchaV2"

# API 地址
CREATE_TASK_ENDPOINT = 'https://api.captcha.run/v2/tasks'
GET_TASK_ENDPOINT = 'https://api.captcha.run/v2/tasks/{task_id}'


def create_task() -> str:
    """创建任务"""
    headers = {'Authorization': f'Bearer {token}'}
    json_data = {
        'captchaType': task_type,
        'siteKey': websiteKey,
        'siteReferer': websiteURL,
    }

    try:
        response = requests.post(CREATE_TASK_ENDPOINT, headers=headers, json=json_data)
        response.raise_for_status()
        result = response.json()
        return result.get('taskId')
    except requests.exceptions.RequestException as e:
        print(f"创建任务出错: {e}")
        return None


def get_response(task_id: str) -> str:
    '''获取结果'''
    headers = {'Authorization': f'Bearer {token}'}
    timeout = 180  # 等待超时时间
    interval = 3   # 每次获取response的间隔时间

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(GET_TASK_ENDPOINT.format(task_id=task_id), headers=headers)
            response.raise_for_status()  # 检查是否出错
            result = response.json()
            solution = result.get('response', {})
            if result.get("status","Fail") == "Fail":
                raise Exception("识别失败")
            if solution and 'gRecaptchaResponse' in solution:
                return solution['gRecaptchaResponse']
            time.sleep(interval)
        except requests.exceptions.RequestException as e:
            print(f"获取任务结果出错: {e}")
            time.sleep(interval)
        except KeyError:
            print(f"服务器返回的响应无效: {result}")
            return None

    print("验证码识别超时!")
    return None


def verify_website(response: str) -> str:
    # 设置你喜欢的浏览器
    driver = webdriver.Chrome(service=Service(r"chromedriver.exe"))
    # 每个网站的注入方式可能都不同，请按需修改
    driver.get("https://www.google.com/recaptcha/api2/demo")
    driver.execute_script(f'document.getElementById("g-recaptcha-response").value="{response}"')
    driver.execute_script(f'onSuccess("{response}")')
    # driver.find_element(value="recaptcha-demo-submit").click()
    time.sleep(999)
    return driver.page_source


if __name__ == '__main__':
    task_id = create_task()
    print('创建任务:', task_id)
    if task_id:
        response = get_response(task_id)
        print('识别结果:', response)
        if response:
            result = verify_website(response)
            print('验证结果：', result)
