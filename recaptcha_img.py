import requests
import base64

token  = "156543ab-4c71-4b59-a531-372581bd7739"

img_dict_zh = {
  '出租车': '/m/0pg52',
  '巴士': '/m/01bjv',
  '公交车': '/m/01bjv',
  '校车': '/m/02yvhj',
  '摩托车': '/m/04_sv',
  '拖拉机': '/m/013xlm',
  '烟囱': '/m/01jk_4',
  '人行横道': '/m/014xcs',
  '红绿灯': '/m/015qff',
  '自行车': '/m/0199g',
  '停车计价表': '/m/015qbp',
  '汽车': '/m/0k4j',
  '小轿车': '/m/0k4j',
  '桥': '/m/015kr',
  '船': '/m/019jd',
  '棕榈树': '/m/0cdl1',
  '山': '/m/09d_r',
  '消防栓': '/m/01pns0',
  '楼梯': '/m/01lynh'
}
img_dict_en = {
  'taxis': '/m/0pg52',
  'bus': '/m/01bjv',
  'school bus': '/m/02yvhj',
  'motorcycles': '/m/04_sv',
  'tractors': '/m/013xlm',
  'chimneys': '/m/01jk_4',
  'crosswalks': '/m/014xcs',
  'traffic lights': '/m/015qff',
  'bicycles': '/m/0199g',
  'parking meters': '/m/015qbp',
  'cars': '/m/0k4j',
  'bridges': '/m/015kr',
  'boats': '/m/019jd',
  'palm trees': '/m/0cdl1',
  'mountains or hills': '/m/09d_r',
  'fire hydrant': '/m/01pns0',
  'stairs': '/m/01lynh'
}


def get_location(encoded_string, img_tag):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    img_dict = {}
    if img_dict_zh.get(img_tag):
        print(img_tag, img_dict_zh[img_tag])
        img_dict = img_dict_zh
    elif img_dict_en.get(img_tag):
        print(img_tag, img_dict_en[img_tag])
        img_dict = img_dict_en
    else:
        return []
    # encoded_string = base64.b64encode(requests.get(imgUrl).content).decode('utf-8')
    # print(encoded_string)
    json_data = {
        'captchaType': 'ReCaptchaV2Classification',
        'image': encoded_string,
        'question': img_dict[img_tag],
    }

    response = requests.post('https://api.captcha.run/v2/tasks', headers=headers, json=json_data).json()
    print(response)
    return response['result']['objects']


# get_location("https://www.google.com/recaptcha/enterprise/payload?p=06AFcWeA4MakjIGaj1NB39o60OaULxFyCZ0BMgcjYsvpMhfyItPNUJ5nIXeABN78bUk-7xrM3Tbt4tOIgnif9c8MwsTH_-lgpafOlh8yWXA1R6TEIRcUoNjDkwSw6aYR39KXCLXn_RrNSNo9hMNK7aMpzP-dZFG76hL-N0p0EXIANEJ8NDN5SldGmZ4QyjMoEMUZqtgALDQ-HaTcp7Xrxq7RsihFq1bAgAfA&k=6Lf0kIIpAAAAAEtyIjCB0tpvGmF_UMCE5r3VVvnG", '')