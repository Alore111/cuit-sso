import requests
import configparser
import time
from loguru import logger
import chaojiying as cjy
from urllib.parse import urlparse, parse_qs

# 配置 loguru 日志格式
logger.add("logfile.log", format="{time} | {level} | {message}", level="DEBUG")

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 从配置文件中获取信息
ACCOUNT = config['ACCOUNT']
CJY = config['CHAOJIYING']
URLS = config['URLS']

def get_cookie():
    url = URLS['login_url']
    params = {"service": URLS['service_url']}
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Te": "trailers"
    }

    try:
        response = requests.post(url, params=params, headers=headers)
        response.raise_for_status()
        cookies = response.cookies.get_dict()
        return {
            "route": cookies.get('route'),
            "SESSION": cookies.get('SESSION')
        }
    except requests.RequestException as e:
        logger.error(f"获取Cookie失败: {e}")
        return None

def get_data_list(cookie):
    url = URLS['data_list_url']
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Cookie": f"route={cookie['route']}; SESSION={cookie['SESSION']}",
    }

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"获取数据列表失败: {e}")
        return None

def get_captcha(timestamp, cookie):
    url = URLS['captcha_url']
    params = {"timestamp": timestamp}
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Cookie": f"route={cookie['route']}; SESSION={cookie['SESSION']}",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Te": "trailers"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(f"获取验证码失败: {e}")
        return None

def loginCheck(username, password, captcha, cookie):
    url = URLS['login_check_url']
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Cookie": f"route={cookie['route']}; SESSION={cookie['SESSION']}",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Te": "trailers"
    }
    params = {
        'name': username,
        'pwd': password,
        'captcha': captcha
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.text == 'success'
    except requests.RequestException as e:
        logger.error(f"登录检查失败: {e}")
        return False

def get_ticket(execution, username, password, captcha, cookie):
    url = f"{URLS['login_url']}?service={URLS['service_url']}"
    headers = {
        'Host': 'sso.cuit.edu.cn',
        "Cookie": f"route={cookie['route']}; SESSION={cookie['SESSION']}",
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://sso.cuit.edu.cn',
        'Referer': f"https://sso.cuit.edu.cn/authserver/login?service={URLS['service_url']}",
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Te': 'trailers',
        'Connection': 'close'
    }
    data = {
        'execution': execution,
        '_eventId': 'submit',
        'lm': 'usernameLogin',
        'geolocation': '',
        'username': username,
        'password': password,
        'captcha': captcha
    }

    try:
        response = requests.post(url, headers=headers, data=data, allow_redirects=False)
        response.raise_for_status()
        redirect_location = response.headers.get('Location')
        set_cookie = response.headers.get('Set-Cookie')
        if redirect_location:
            parsed_url = urlparse(redirect_location)
            ticket = parse_qs(parsed_url.query).get('ticket', [None])[0]
            cookieTGC = set_cookie.split(';')[0].split('=')[1]
            return ticket, cookieTGC
        else:
            logger.error("重定向地址中没有找到ticket")
            return None, None
    except requests.RequestException as e:
        logger.error(f"获取票据失败: {e}")
        return None, None


if __name__ == "__main__":
    chaojiying = cjy.Chaojiying_Client(CJY['username'], CJY['password'], CJY['soft_id'])
    cookie = get_cookie()
    if cookie:
        logger.info(f"获取到cookie：{cookie}")
        dataList = get_data_list(cookie)
        logger.info(f"获取到数据")
        for attempt in range(3):
            timestamp = str(int(time.time() * 1000))
            cap = get_captcha(timestamp, cookie)
            if cap:
                with open("captcha.jpg", "wb") as f:
                    f.write(cap.content)
                img = cap.content
                captcha_str = chaojiying.PostPic(img, 1004)["pic_str"]
                logger.info(f"验证码识别结果：{captcha_str}")
                isLogin = loginCheck(ACCOUNT['username'], ACCOUNT['password'], captcha_str, cookie)
                logger.info(f"登录结果：{isLogin}")
                if isLogin:
                    ticket, tgc = get_ticket('e1s1', ACCOUNT['username'], ACCOUNT['password'], captcha_str, cookie)
                    if ticket and tgc:
                        logger.info(f"获取到ticket：{ticket}")
                        logger.info(f"获取到cookieTGC：{tgc}")
                        break
                    else:
                        logger.error("获取ticket或cookie失败")
                else:
                    logger.error(f"登录失败，第{attempt + 1}次重试")
            else:
                logger.error("获取验证码失败")
        else:
            logger.error("登录失败次数达到上限")
    else:
        logger.error("获取cookie失败")


