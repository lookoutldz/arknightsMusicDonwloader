import json
import os.path
import urllib.parse

import requests
from requests.exceptions import ProxyError, SSLError
from retrying import retry
from tqdm import tqdm

domain = 'https://arknightsost.nbh.workers.dev'
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/98.0.4758.80 Safari/537.36',
    'accept-language': 'zh-CN,zh;q=0.9'
}
folder = 'bgm'


# 深度优先下载文件
# 1：如果 obj 是文件链接直接下载返回
# 2：如果 obj 是文件夹，则请求链接，拿到文件夹内的内容（obj list），迭代 dfs(obj)
def dfs(parent, obj):
    name = obj['name']
    path = folder + parent + name
    if parent != '' and os.path.exists(path):
        if 'size' in obj and fully_downloaded(path, int(obj['size'])):
            return
    file_url = domain + parent + urllib.parse.quote(name)
    dir_url = file_url + '/'
    if 'size' in obj:
        size = int(obj['size'])
        offset = resume_offset(path, size)
        if offset != 0:
            headers['Range'] = 'bytes=' + str(offset) + '-'
        downloads(path, file_url, size, offset)
    else:
        mkdir(path)
        try:
            data = getfiles(dir_url)
            for sub in iter(data):
                dfs(parent + name + '/', sub)
        except ProxyError:
            print('Network Error (PROXY) for url: ' + dir_url)
        except SSLError:
            print('Network Error (SSL) for url: ' + dir_url)


# 获取文件目录
@retry(stop_max_attempt_number=5, stop_max_delay=30)
def getfiles(url):
    obj = json.loads(requests.post(url, headers).text)
    if obj is not None and 'files' in obj:
        return obj['files']
    else:
        return []


# 是否已经下载了完整的文件
def fully_downloaded(path, size):
    if size - os.path.getsize(path) == 0:
        print('fully downloaded: ' + path)
        return True
    return False


# 断点续传偏移量
def resume_offset(path, size):
    if not os.path.exists(path):
        return 0
    elif size - os.path.getsize(path) < 0:
        return 0
    else:
        return size - os.path.getsize(path)


# 下载内容
def downloads(filename, url, size, offset):
    response = requests.post(url, headers)
    if response.status_code == 206:
        # 服务器支持断点续传
        write_to_file(filename, 'a', response, size, offset)
    elif response.status_code == 200:
        # 服务器不支持断点续传
        write_to_file(filename, 'wb', response, size, offset)
    else:
        # 下载失败
        print('statusCode[' + str(response.status_code) + '] for [' + filename + ']\n')


# 写入文件
def write_to_file(filename, level, response, size, offset):
    # 进度条显示
    pbar = tqdm(total=size, initial=offset, unit='b', unit_scale=True, desc=filename)
    with open(filename, level) as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                offset += len(chunk)
                f.write(chunk)
                f.flush()
                pbar.update(len(chunk))
                pbar.refresh()
    pbar.close()


# 新建文件夹
def mkdir(dir_name):
    if dir_name != '' and not os.path.exists(dir_name):
        os.mkdir(dir_name)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Starting...\n')
    mkdir(folder)
    dfs('', {'name': ''})
    print('\nFinished.')
