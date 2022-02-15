# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import json
import os.path
import urllib.parse

import requests
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
# 2：如果 url 是文件夹，则请求链接，拿到文件夹内的内容（obj list），for 循环迭代 dfs(obj)
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
        data = getfiles(dir_url)
        for sub in iter(data):
            dfs(parent + name + '/', sub)


@retry(stop_max_attempt_number=5, stop_max_delay=30)
def getfiles(url):
    obj = json.loads(requests.post(url, headers).text)
    if obj is not None:
        if 'files' not in obj:
            return []
        else:
            return obj['files']
    else:
        return []


def fully_downloaded(path, size):
    if size - os.path.getsize(path) == 0:
        print('fully downloaded: ' + path)
        return True
    return False


def resume_offset(path, size):
    if not os.path.exists(path):
        return 0
    elif size - os.path.getsize(path) < 0:
        return 0
    else:
        return size - os.path.getsize(path)


def downloads(filename, url, size, offset):
    data = requests.post(url, headers)
    pbar = tqdm(total=size, initial=offset, unit='b', unit_scale=True, desc=filename)
    if data.status_code == 206:
        with open(filename, 'a') as f:
            for chunk in data.iter_content(chunk_size=1024):
                if chunk:
                    offset += len(chunk)
                    f.write(chunk)
                    f.flush()
                    pbar.update(len(chunk))
                    pbar.refresh()
    elif data.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in data.iter_content(chunk_size=1024):
                if chunk:
                    offset += len(chunk)
                    f.write(chunk)
                    f.flush()
                    pbar.update(len(chunk))
                    pbar.refresh()
    else:
        print('statusCode[' + str(data.status_code) + '] for [' + filename + ']\n')
    pbar.close()


def mkdir(dirname):
    if dirname != '' and not os.path.exists(dirname):
        os.mkdir(dirname)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Starting...\n')
    mkdir(folder)
    dfs('', {'name': ''})
    print('\nFinished.')