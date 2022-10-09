import requests
import re
import time
from multiprocessing.pool import Pool


class Client:
    def __init__(self, **headers):
        self.headers = headers
    
    def request(self, url):
        return requests.get(url, headers=self.headers)


def download_ts(client, url, decrypt, **kwargs):
    global lock
    response = client.request(url)
    ts_bytes = response.content
    if decrypt is not None:
        ts_bytes = decrypt(ts_bytes, **kwargs)
    return ts_bytes


class M3U8:
    def __init__(self, client, url):
        self.client = client
        self.url_pre = url[:url.rfind('/')+1]
        response = self.client.request(url)
        assert response.reason == 'OK', 'failed to get content, response:' + response.reason
        self.text = str(response.content, 'UTF-8')
        self.is_ts_list = True
        self.is_encrypted = False
        if '#EXT-X-KEY' in self.text:
            self.is_encrypted = True
            print('ENCRYPTED')
        if '.m3u8' in self.text:
            self.is_ts_list = False
        self.child_urls = []
        for line in self.text.split('\n'):
            if '#EXT' not in line and len(line) > 0:
                if 'http' not in line:
                    self.child_urls.append(self.url_pre + line)
                else:
                    self.child_urls.append(line)
    
    def get_m3u8(self, index, client=None):
        if self.is_ts_list:
            print('this is a ts list')
            return None
        if client is None:
            client = self.client
        return M3U8(client, self.child_urls[index])
    
    def get_ts(self, file_path, decrypt=None, **kwargs):
        if not self.is_ts_list:
            print('this is a m3u8 list')
            return
        if len (file_path) - file_path.rfind('.ts') != 3:
            print('file path should end with .ts')
            return
        t1 = time.time()
        results = []
        pool = Pool()
        for cu in self.child_urls:
            results.append(pool.apply_async(download_ts, (self.client, cu, decrypt), kwargs))
        pool.close()
        pool.join()
        with open(file_path, 'wb') as f:
            for r in results:
                f.write(r.get())    # ApplyResult
        t2 = time.time()
        print('total time:', t2 - t1)
        return


test_url = 'http://devimages.apple.com/iphone/samples/bipbop/bipbopall.m3u8'


if __name__ == '__main__':
    m3u8 = M3U8(Client(), test_url)
    m3u8 = m3u8.get_m3u8(2)
    m3u8.get_ts('/Users/test.ts')
