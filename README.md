# CUIT-SSO

### 项目简介

本项目旨在自动化CUIT统一身份认证系统的登录过程，包括验证码识别。项目支持多种验证码识别方式，并使用Python模拟登录流程。

### 功能特点

- 管理Cookie以维持会话。
- 支持多种验证码识别方法：
  - **超级鹰（Chaojiying）**：在线验证码识别服务。
  - **ddddocr**：开源OCR库用于验证码识别。
  - **手动输入**：如果自动识别失败，保存验证码图片供手动输入。
- 使用 `loguru` 进行日志管理。

### 开发计划

- [x] 支持手动输入验证码。
- [x] 支持使用超级鹰识别验证码。
- [x] 支持使用ddddocr识别验证码。
- [x] 支持使用Cookie管理会话。
- [ ] 支持获取教务处任意页面（get_page待修复）。
- [ ] 支持WebVPN登录。
- [ ] 支持使用代理IP。
- [ ] 支持使用第三方登录。

### 环境要求

- Python 3.10+
- 所需库：`requests`, `configparser`, `loguru`, `ddddocr`

### 安装步骤

1. **克隆项目仓库：**
   ```sh
   git clone https://github.com/Alore111/cuit-sso.git
   cd cuit-sso
   ```

2. **创建并激活虚拟环境（venv）：**
   ```sh
   python -m venv venv
   source venv/bin/activate  # 对于Windows用户，使用 `venv\Scripts\activate`
   ```

3. **安装依赖：**
   ```sh
   pip install -r requirements.txt
   ```

4. **配置设置：**

   编辑 `config.ini` 文件以设置账户信息和服务URL。文件格式如下：

   ```ini
    # 验证码识别方式
    # 1: 超级鹰在线识别（需注册超级鹰账号并获取题分）
    # 2: 开源学习库本地识别（ddddocr第三方库）
    # 3：手动输入（验证码图片位于captcha.jpg）
    [CAPTCHA]
    crack_type = 2

    # 超级鹰账号密码（若未选择此方式可不填）
    # 需注册超级鹰账号并获取题分
    # https://www.chaojiying.com/
    [CHAOJIYING]
    username = your_cjy_username
    password = your_cjy_password
    soft_id = your_cjy_soft_id

    [URLS]
    login_url = https://sso.cuit.edu.cn/authserver/login
    data_list_url = https://sso.cuit.edu.cn/authserver/data/list
    captcha_url = https://sso.cuit.edu.cn/authserver/captcha
    login_check_url = https://sso.cuit.edu.cn/authserver/loginCheck
    service_url = http://jwgl.cuit.edu.cn/eams/login.action
    act_elect_course = http://jwgl.cuit.edu.cn/eams/stdElectCourse.action
   ```

### 使用方法

1. **激活虚拟环境：**
   ```sh
   source venv/bin/activate  # 对于Windows用户，使用 `venv\Scripts\activate`
   ```

2. **运行脚本：**
   ```sh
   python suitsso.py
   ```

3. **手动输入验证码（如果配置）：**
   - 如果选择手动输入验证码（crack_type = 3），验证码图片将保存到项目目录中的 `captcha.jpg` 文件。你需要查看该图片并在提示时手动输入验证码。

### 代码概览

- **CUITSSO 类：** 包含处理登录过程的所有方法，包括获取Cookie、处理验证码和提交登录表单。
- **suitsso.py：** 初始化登录过程并配置日志。

### 方法概述

- `get_cookie()`: 获取初始会话Cookie。
- `get_data_list()`: 使用会话Cookie获取数据列表。
- `get_captcha(timestamp)`: 获取验证码图片。
- `login_check(captcha)`: 使用提供的验证码检查登录状态。
- `get_ticket(execution, captcha)`: 成功验证码验证后获取登录票据。
- `get_jsession()`: 获取 `jsession` Cookie。
- `get_gsession()`: 获取 `gsession` Cookie。
- `login()`: 执行登录过程的主函数。

### 日志管理

日志将保存到 `logfile.log` 文件中，包括过程中的详细信息。

### 验证码处理

脚本支持三种验证码识别方式：

1. **超级鹰（crack_type = 1）**
2. **ddddocr（crack_type = 2）**
3. **手动输入（crack_type = 3）**

修改 `config.ini` 中的 `crack_type` 值以选择所需的识别方法。

### 配置示例 (`config.ini`)

```ini
# 验证码识别方式
# 1: 超级鹰在线识别（需注册超级鹰账号并获取题分）
# 2: 开源学习库本地识别（ddddocr第三方库）
# 3：手动输入（验证码图片位于captcha.jpg）
[CAPTCHA]
crack_type = 2

# 超级鹰账号密码（若未选择此方式可不填）
# 需注册超级鹰账号并获取题分
# https://www.chaojiying.com/
[CHAOJIYING]
username = your_cjy_username
password = your_cjy_password
soft_id = your_cjy_soft_id

[URLS]
login_url = https://sso.cuit.edu.cn/authserver/login
data_list_url = https://sso.cuit.edu.cn/authserver/data/list
captcha_url = https://sso.cuit.edu.cn/authserver/captcha
login_check_url = https://sso.cuit.edu.cn/authserver/loginCheck
service_url = http://jwgl.cuit.edu.cn/eams/login.action
act_elect_course = http://jwgl.cuit.edu.cn/eams/stdElectCourse.action
```

### 注意事项

- 如果使用超级鹰进行验证码识别，请确保拥有有效的超级鹰账户。
- ddddocr库可能占用较多内存。
- 手动输入需要用户交互来输入验证码。

### 贡献

欢迎Fork此仓库，进行改进并提交Pull Request。非常欢迎各类贡献！

### 许可证

此项目采用GPL许可证。详情请参阅LICENSE文件。

### 联系方式

如有任何问题或需要帮助，请在GitHub上提出Issue或联系 [alore@2ndtool.top]。

### 声明

本脚本仅用于学习交流，不得用于任何商业用途。使用本脚本造成的任何后果，与本作者无关。