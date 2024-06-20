import contextlib
import io
import requests
import configparser
import time
from loguru import logger
import chaojiying as cjy
from urllib.parse import urlparse, parse_qs
import ddddocr

# 配置 loguru 日志格式
logger.add("logfile.log", format="{time} | {level} | {message}", level="DEBUG")

class CUITSSO:
    def __init__(self, username, password):
        # 读取配置文件
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf-8')

        # 从配置文件中获取信息
        self.ACCOUNT = self.config['ACCOUNT']
        self.CJY = self.config['CHAOJIYING']
        self.CAPTCHA = self.config['CAPTCHA']
        self.URLS = self.config['URLS']

        # 初始化用户信息
        self.username = username
        self.password = password
        self.crack_type = int(self.CAPTCHA['crack_type'])
        self.cookie = None
        self.ticket = None
        self.tgc = None
        self.jsession = None
        self.gsession = None

        # 如果验证码破解类型为1，初始化超级鹰客户端
        if self.crack_type == 1:
            self.chaojiying = cjy.Chaojiying_Client(self.CJY['username'], self.CJY['password'], self.CJY['soft_id'])

    def get_cookie(self):
        # 获取初始Cookie
        url = self.URLS['login_url']
        params = {"service": self.URLS['service_url']}
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
            self.cookie = {
                "route": cookies.get('route'),
                "SESSION": cookies.get('SESSION')
            }
        except requests.RequestException as e:
            logger.error(f"获取Cookie失败: {e}")
            self.cookie = None

    def get_data_list(self):
        # 获取数据列表
        url = self.URLS['data_list_url']
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": f"route={self.cookie['route']}; SESSION={self.cookie['SESSION']}",
        }

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"获取数据列表失败: {e}")
            return None

    def get_captcha(self, timestamp):
        # 获取验证码图片
        url = self.URLS['captcha_url']
        params = {"timestamp": timestamp}
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": f"route={self.cookie['route']}; SESSION={self.cookie['SESSION']}",
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

    def login_check(self, captcha):
        # 验证登录信息
        url = self.URLS['login_check_url']
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": f"route={self.cookie['route']}; SESSION={self.cookie['SESSION']}",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Te": "trailers"
        }
        params = {
            'name': self.username,
            'pwd': self.password,
            'captcha': captcha
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.text == 'success'
        except requests.RequestException as e:
            logger.error(f"登录检查失败: {e}")
            return False

    def get_ticket(self, execution, captcha):
        # 获取票据（ticket）
        url = f"{self.URLS['login_url']}?service={self.URLS['service_url']}"
        headers = {
            'Host': 'sso.cuit.edu.cn',
            "Cookie": f"route={self.cookie['route']}; SESSION={self.cookie['SESSION']}",
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://sso.cuit.edu.cn',
            'Referer': f"https://sso.cuit.edu.cn/authserver/login?service={self.URLS['service_url']}",
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
            'username': self.username,
            'password': self.password,
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
                self.ticket = ticket
                self.tgc = set_cookie.split(';')[0].split('=')[1]
            else:
                logger.error("重定向地址中没有找到ticket")
        except requests.RequestException as e:
            logger.error(f"获取票据失败: {e}")
            self.ticket = None
            self.tgc = None

    def get_jsession(self):
        # 获取JSESSIONID
        url = f"{self.URLS['act_elect_course']}"
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
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            self.jsession = response.headers.get('Set-Cookie').split(';')[0].split('=')[1]
        except requests.RequestException as e:
            logger.error(f"获取jsession失败: {e}")
            self.jsession = None

    def get_gsession(self):
        # 获取GSESSIONID
        url = f"{self.URLS['act_elect_course']}"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Cookie": "JSESSIONID=" + self.jsession,
            "Upgrade-Insecure-Requests": "1",
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            self.gsession = response.headers.get('Set-Cookie').split(';')[0].split('=')[1]
        except requests.RequestException as e:
            logger.error(f"获取gsession失败: {e}")
            self.gsession = None

    def login(self):
        # 登录过程，包含获取Cookie、验证码、登录校验和票据
        self.get_cookie()
        if self.cookie:
            for attempt in range(3):
                timestamp = str(int(time.time() * 1000))
                cap = self.get_captcha(timestamp)
                if cap:
                    with open("captcha.jpg", "wb") as f:
                        f.write(cap.content)
                    img = cap.content
                    if self.crack_type == 1:
                        captcha_str = self.chaojiying.PostPic(img, 1004)["pic_str"]
                        logger.info(f"验证码识别结果：{captcha_str}")
                    elif self.crack_type == 2:
                        # 初始化 ddddocr 对象，抑制输出消息
                        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                            ocr = ddddocr.DdddOcr()
                            captcha_str = ocr.classification(img)
                            logger.info(f"验证码识别结果：{captcha_str}")
                    else:
                        captcha_str = input("请输入验证码(图片位于captcha.jpg)：")
                    
                    is_login = self.login_check(captcha_str)
                    # logger.info(f"登录结果：{is_login}")
                    if is_login:
                        self.get_ticket('e1s1', captcha_str)
                        self.get_jsession()
                        if self.jsession:
                            self.get_gsession()
                        if self.ticket and self.tgc:
                            logger.success("登录成功")
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


if __name__ == "__main__":
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    # 从配置文件中获取信息
    ACCOUNT = config['ACCOUNT']

    # 初始化 CUITSSO 对象
    cuit_login = CUITSSO(ACCOUNT['username'], ACCOUNT['password'])
    cuit_login.login()
    
    # 输出登录信息
    logger.info(f"gsession: {cuit_login.gsession}")
    logger.info(f"jsession: {cuit_login.jsession}")
    logger.info(f"ticket: {cuit_login.ticket}")
    logger.info(f"tgc: {cuit_login.tgc}")
    logger.info(f"cookie: {cuit_login.cookie}")
