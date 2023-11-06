# %% [markdown]
# ### 具体实践：在[四六级试卷网站](https://pan.uvooc.com/)获取下载链接并批量下载
# #### 存在问题(已解决)：
# 1. 网站呈现目录形式，部分链接是访问后进入下一级，而不是直接的下载链接；  
# （后者链接中似乎包含pdf/.mp3等+?请求信息，可以如此筛选，实现循环）；  
# 1. 全部文件都下载在一个文件夹，可考虑一方面循环下载时下载在新的文件夹；  
# （循环前在非下载链接时创建文件夹），另一方面以年、月、卷识别文件，自动分至文件夹；  
# 1. 文件名内以“卷一”形式标记，文件目录不会按照一二三排序，可更名为卷1/2/3；  
# 1. 网站需要向下翻页加载剩余内容，需要搜集相关操作；  
# 1. 运行时，弹出的提示框挡住了控件，无法点击控件。

# %%
#建类
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.keys import Keys
import time
 
class SeleniumHelper:
    def __init__(self, driver):
        self.driver = driver
 
    def find_element(self, locator, timeout=10):
        """
        查找单个元素
        :param locator: 元素定位信息，如(By.ID, 'element_id')
        :param timeout: 超时时间，默认为10秒
        :return: WebElement对象或None
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except (TimeoutException, NoSuchElementException):
            return None
 
    def find_elements(self, locator, timeout=10):
        """
        查找多个元素
        :param locator: 元素定位信息，如(By.CLASS_NAME, 'element_class')
        :param timeout: 超时时间，默认为10秒
        :return: WebElement对象列表或空列表
        """
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located(locator)
            )
            return elements
        except (TimeoutException, NoSuchElementException):
            return []


# %%
#等待弹窗消失
def check_popup(driver):
    begin=stop=0
    second=0
    while True:
        time.sleep(0.5)
        popup=driver.find_element(By.CSS_SELECTOR,'.hope-notification__list.hope-c-UdTFD.hope-c-UdTFD-jEXiZO-placement-top-end.hope-c-PJLV.hope-c-PJLV-ijhzIfm-css')
        second+=0.5
        if "通知" in popup.text and begin==0:begin=second
        elif "通知" not in popup.text and begin !=0:stop=1;print(f"耗时{second-begin}秒弹框消失");return 

# %%
import queue,pyperclip,os
from selenium.webdriver.common.action_chains import ActionChains
first=[2]
# 创建新默认路径与下载设置未能实现，请每次更新一下下载地址
download_path=r"files"
modified_path=r"modified_files"

url="https://pan.uvooc.com/Learn/CET/CET6"
#测试链接（内容较少）："https://pan.uvooc.com/Music/Favor"
visited_links = set()  # 存储已访问的链接
link_queue = queue.Queue()  # 存储待访问的链接的队列
# 将初始链接添加到队列
link_queue.put(url)

url_text={url:os.path.join(modified_path,"CET6")}#请自行设置初始文件夹名

import os,subprocess,psutil
# 切换到浏览器安装地址
os.chdir("C:\Program Files (x86)\Microsoft\Edge\Application")
# 启动9222端口以D:\chrome\seleniumEdge路径作为自定义用户数据目录
sub_popen = subprocess.Popen('.\msedge.exe --remote-debugging-port=9222 --user-data-dir="D:\chrome\seleniumEdge"')
while True:
    if "msedge.exe" in [p.name() for p in psutil.process_iter()]:
        break
    
edge_options = webdriver.EdgeOptions()
edge_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
# 浏览器引擎路径 + 自定义浏览器配置
driver = webdriver.Edge(options=edge_options)

# 创建SeleniumHelper对象
helper = SeleniumHelper(driver)
#input()

def carry_out(helper,parent_path):
    # 查找并点击所有指定的元素name hope-text hope-c-PJLV hope-c-PJLV hope-c-PJLV-ieThUYk-css
    elements = helper.find_elements((By.CLASS_NAME, 'hope-c-PJLV-ieThUYk-css'))
    print(f"elements:{elements}")
    
    for element in elements[first[0]:]:
        if first==[2]:first[0]=0
        print(element.text)
        action_chains = ActionChains(driver)
        # 右键点击元素
        action_chains.context_click(element).perform()
        # 查找复制链接的元素并点击
        copy_link_element = helper.find_element((By.CLASS_NAME, 'solid-contextmenu__item'))
        if copy_link_element:
            copy_link_element.click()

            # 等待一段时间以确保复制操作完成
            time.sleep(1)

            # 获取剪贴板内容（需要安装pyperclip库）
            
            clipboard_content = pyperclip.paste()
            link_queue.put(clipboard_content)
            url_text[clipboard_content]=os.path.join(parent_path,element.text)
            # 打印复制的链接
            #print("复制的链接：", clipboard_content)

def find_by_loop(driver,parent_path):
    body = driver.find_element(By.TAG_NAME, "body")
    # 初始滚动位置
    previous_scroll_position = 0
    # 定义等待时间
    scroll_interval = 0.5

    while True:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(scroll_interval)

        # 检查是否到达页面底部
        current_scroll_position = driver.execute_script("return window.pageYOffset;")
        
        #print(current_scroll_position ,previous_scroll_position)
        if current_scroll_position == previous_scroll_position:
            print("已到达页面底部,加载完毕内容")
            break
    
        previous_scroll_position = current_scroll_position
            
    carry_out(helper,parent_path)

    time.sleep(scroll_interval)
    

while not link_queue.empty():
    # 取出下一个链接
    current_link = link_queue.get()
    print(f"----正在访问{current_link}")
    # 检查链接是否已访问过
    if current_link in visited_links:
        continue
    
    # 访问链接
    driver.get(current_link)
    visited_links.add(current_link)
    
    #是文件就直接下载结束
    if "?" in current_link:
        print(f"该链接为下载链接，正在下载")
        parent_path=os.path.dirname(url_text[current_link])
        print(url_text[current_link])

        while  len(os.listdir(download_path))>0 :#
            time.sleep(0.5)
            print("...下载中...loading...")
            if (os.listdir(download_path)[0]).endswith(("tmp","crdownload")):continue
            file_name=os.path.basename(os.listdir(download_path)[0])
            os.rename(os.path.join(download_path,os.listdir(download_path)[0]),os.path.join(parent_path,file_name))
            
        print("下载完毕,已移动至对应目录下")
        time.sleep(3)
        continue;#;continue;"""
        #根据传输的目录来移动文件。或者考虑直接join到url_text中？
    #是文件夹，就访问以获得新链接，在页面中查找新链接并添加到队列
    #是文件夹，要创建本地文件夹
    else:
        check_popup(driver)
        print(f"该链接为文件夹链接，正在打开并获取下载链接")
        if not os.path.exists(url_text[current_link]):os.mkdir(url_text[current_link])
        find_by_loop(driver,url_text[current_link])

    #if len(visited_links)>=3:break

print("循环结束，没有新链接可访问")
#driver.quit()



