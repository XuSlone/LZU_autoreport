#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options # 引入Options类
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
#from retrying import retry
import sys
import logging
#path = r'C:\Users\ASUS\Desktop\chromedriver.exe' 


# In[5]:


#打卡用户信息
#sys.argv

username = sys.argv[1]
password = sys.argv[2]


# In[3]:


#初始化日志模块
logger = logging.getLogger(username)
logger.setLevel('INFO')
BASIC_FORMAT = "%(asctime)s:%(name)s:%(levelname)s:%(message)s"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
chlr = logging.StreamHandler() # 输出到控制台的handler
chlr.setFormatter(formatter)
chlr.setLevel('INFO')  # 也可以不设置，不设置就默认用logger的level
fhlr = logging.FileHandler(username+'.log') # 输出到文件的handler
fhlr.setFormatter(formatter)
logger.addHandler(chlr)
logger.addHandler(fhlr)


# In[4]:


chrome_options = Options() # 创建一个参数对象
chrome_options.add_argument('--headless')  # 无界面
chrome_options.add_argument('--no-sandbox')  # 解决DevToolsActivePort文件不存在报错问题
chrome_options.add_argument('--disable-gpu')   # 禁用GPU硬件加速。如果软件渲染器没有就位，则GPU进程将不会启动。
chrome_options.add_argument('--disable-dev-shm-usage')
prefs = {"profile.managed_default_content_settings.images": 2} #不加载图片
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument('--window-size=1920,1080')         # 设置当前窗口的宽度和高度

#启动浏览器
logger.info("正在初始化..............")
driver = webdriver.Chrome('chromedriver', options=chrome_options)
driver.get("http://my.lzu.edu.cn:8080/login?service=http://my.lzu.edu.cn")

#填写账号密码 
logger.info("正在登录................")
driver.find_element_by_id("username").click()
driver.find_element_by_id("username").clear()
driver.find_element_by_id("username").send_keys(username)
driver.find_element_by_id("password").clear()
driver.find_element_by_id("password").send_keys(password)
driver.find_element_by_xpath("//form[@id='loginForm']/div[4]/button").click()

#获取用户信息
try:
    name_div = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"userName\"]")))
    time.sleep(1)
    logger.info(name_div.text+"——登录成功！")
except:
    logger.warning("登录失败！请检查用户名和密码！")
    
    exit()

#尝试去点击进入
attempts = 0
success = False
close = False
while attempts < 3 and not success:
    try:
        #等待健康打卡按钮加载完成，鼠标移动过去
        logger.info("正在加载健康打卡页面....")
        ActionChains(driver).move_to_element(WebDriverWait(driver,5).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"my-apps\"]/li[1]/a/div[2]/span")))).perform()
    
        #等待进入按钮出来，去点击
        enter_click = WebDriverWait(driver, 5).until( 
                EC.element_to_be_clickable((By.XPATH, "//ul[@id='my-apps']/li/a/div[2]/p[2]/span")))
        enter_click.click()
        success = True
    except Exception as e:
        print(e)
        attempts += 1
        if attempts == 3:
            logger.error("等待超时，请检查网络！")
            driver.close()
            close==True
            break

if not close:
    #等待frame加载出来切换到iframe里
    WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iframe")))

#     driver.switch_to.frame("iframe")

    # 检查是否打卡完成
    logger.info("正在检测填报状态........")
    finshflag=False
    try:
        finsh_div = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "/html/body/uni-app/uni-modal/div[2]/div[2]")))
        if "完成" in finsh_div.text:
            logger.info("当日填报完成!守护兰大，抗疫有你！")
            finshflag=True
    except :
        logger.warning("当日未填报！")

    #没上报的话就点上报
    if not finshflag: 
        logger.info("正在为您打卡..............")
        driver.find_element_by_xpath("/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[3]/uni-view/uni-form/span/uni-view[12]/uni-button").click()
        report_result = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "/html/body/uni-app/uni-modal/div[2]/div[2]")))
        logger.info("健康打卡成功!守护兰大，抗疫有你")

    driver.close()


# In[ ]:




