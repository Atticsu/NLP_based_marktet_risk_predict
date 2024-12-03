#%%
import re
import requests
import pandas as pd
from tqdm import tqdm
import time
import json
import requests
import random
import os
import warnings
warnings.filterwarnings("ignore")

#%%
url = "https://zhibo.sina.com.cn/api/zhibo/feed"
id = '3810300' #TODO 控制爬取起始点 如需持续更新需要想办法获取（可能通过selenium）
folder_path = '新浪财经' 
os.makedirs(folder_path)

# 读取本地最后的文件
largest_file = None
largest_page_number = -1


for filename in os.listdir(folder_path):
    if filename.endswith('.xlsx'):
        match = re.search(r'page_(\d+)', filename)
        if match:
            page_number = int(match.group(1))  

            if page_number > largest_page_number:
                largest_page_number = page_number
                largest_file = filename

for page in tqdm(range(largest_page_number, 21897)):
    params = {
        "callback": "jQuery111204099375957405327_1728549693503",
        "page": f"{page}",  # 控制页码  #第一次读取从0开始即可
        "page_size": "100",
        "zhibo_id": "152",
        "tag_id": "0",
        "dire": "f",
        "dpc": "1",
        "pagesize": "20",
        "id": f"{id}",  # 控制起始点 
        "type": "1",
        "_": "1728548236210"
    }

    # 构造请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Referer": "https://finance.sina.com.cn/",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd"
    }

    response = requests.get(url, params=params, headers=headers)

    jsonp_data = response.text
    json_data = re.search(r"jQuery\d+_\d+\((.*)\)", jsonp_data).group(1)

    output_string = re.sub(r'\);}catch\(e', '', json_data)
    data = json.loads(output_string)
    df = pd.DataFrame(data['result']['data']['feed']['list'])
    df['tag_str'] = df['tag'].apply(lambda x: str(x))
    df = df[df['tag_str'].str.contains('焦点')]  # 只选择重要新闻
    def clean_string(value):
        if isinstance(value, str):
            return re.sub(r'[\x00-\x1F\x7F]', '', value)  # 去除非法字符
        return value
    df = df.applymap(clean_string)
    df.to_excel(f"新浪财经/id_{id}_page_{page}.xlsx", index=False)
    time.sleep(random.randint(3, 5))
#%%读取最新数据 （不指定ID参数即可)
url = "https://zhibo.sina.com.cn/api/zhibo/feed"
params = {
    "callback": "jQuery111204099375957405327_1728549693503",
    "page": f"0",  # 控制页码 
    "page_size": "100", 
    "zhibo_id": "152",
    "tag_id": "0",
    "dire": "f",
    "dpc": "1",
    # "id": f"{id}",  # 不指定ID参数即是从最新开始
    "pagesize": "20",
    "type": "1",
    "_": "1728548236210"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Referer": "https://finance.sina.com.cn/",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd"
}
response = requests.get(url, params=params, headers=headers)
jsonp_data = response.text
json_data = re.search(r"jQuery\d+_\d+\((.*)\)", jsonp_data).group(1)
output_string = re.sub(r'\);}catch\(e', '', json_data)
data = json.loads(output_string)

# 将数据转换为DataFrame
df = pd.DataFrame(data['result']['data']['feed']['list'])
df['tag_str'] = df['tag'].apply(lambda x: str(x))
df = df[df['tag_str'].str.contains('焦点')]  # 只选择重要新闻
df

# %%
