#%%
import requests
import pandas as pd
import os
import time
from tqdm import tqdm
import re
#%%
output_dir = 'ths_comments_sh'
os.makedirs(output_dir, exist_ok=True)

# 获取已有文件的 pid 和 mtime，并返回最早日期对应的 pid 和 mtime
def get_existing_files(output_dir):
    existing_files = os.listdir(output_dir)
    files_data = []
    pattern = r'(\d+)_(\d+)\.xlsx'
    
    for file in existing_files:
        match = re.match(pattern, file)
        if match:
            pid = match.group(1)
            mtime = int(match.group(2))
            files_data.append((pid, mtime))
    
    if files_data:
        files_data.sort(key=lambda x: x[1])  
        return files_data[0] 
    return None, None

def get_comments_data(pid, mtime):
    url = 'https://t.10jqka.com.cn/lgt/post/open/api/forum/post/v2/recent'
    params = {
        'page': 2,
        'page_size': 15,
        'pid': f'{pid}',
        'time': f'{mtime}',
        'sort': 'reply',
        'code': '1A0001',
        'market_id': 16
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 hxFont/normal getHXAPPAdaptOldSetting/0 Language/zh-Hans getHXAPPAccessibilityMode/0 hxnoimage/0 getHXAPPFontSetting/normal VASdkVersion/1.2.1 VoiceAssistantVer/0 hxtheme/0 IHexin/11.60.62 (Royal Flush) userid/602180054 innerversion/I037.08.531 build/11.60.62 surveyVer/0 isVip/0',
    }
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    df = pd.DataFrame(data['data']['feed'])
    df['pub_time'] = pd.to_datetime(df['mtime'], unit='s', utc=True)
    df['pub_time'] = df['pub_time'].dt.tz_convert('Asia/Shanghai').dt.strftime('%Y-%m-%d %H:%M:%S')
    df.reindex(columns=['pub_time','content']).to_excel(f"{output_dir}/{str(pid)}_{str(mtime)}.xlsx", index=False)
    return df 

last_pid, last_mtime = get_existing_files(output_dir)

# 如果没有已有文件，从初始值开始
if last_pid is None or last_mtime is None:
    pid = '2165876225'
    mtime = '1732600741'
else:
    pid = last_pid
    mtime = str(last_mtime)

# 从最早的 mtime 开始循环抓取数据 无限循环
while True:
    try:
        df = get_comments_data(str(pid), str(mtime))
        pid = df['pid'].iloc[-1]
        mtime = df['mtime'].iloc[-1]
        time.sleep(1)
    except Exception as e:
        print(f'Error occurred: {e}')
        continue