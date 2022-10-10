import requests
from types import FunctionType
from tqdm import tqdm
from multiprocessing.pool import Pool
from time import sleep
from random import uniform


class Client:
    def __init__(self, **headers):
        self.headers = headers
    
    def request(self, url):
        return requests.get(url, headers=self.headers)


def download_ts(client: Client, url: str, decrypt: FunctionType, **kwargs) -> bytes:
    """
    download and decrypt(if needed) .ts
    """
    response = client.request(url)
    ts_bytes = response.content
    if decrypt is not None:
        ts_bytes = decrypt(ts_bytes, **kwargs)
    return ts_bytes


def decrypt_func(ts_bytes: bytes, **kwargs) -> bytes:
    """
    implement based on specific needs
    """
    return ts_bytes


class M3U8:
    def __init__(self, client: Client, url: str):
        """
        get .m3u8 content
        .m3u8 usually contains a certain number of urls of either .m3u8 or .ts
        '#EXT-X-KEY:METHOD=...' means encrypted
        """
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
    
    def print(self):
        """
        print .m3u8 content
        """
        print(self.text)
    
    def get_m3u8(self, index, client=None):
        """
        return a M3U8 created with certain url in the url list
        """
        if self.is_ts_list:
            print('this is a .ts list')
            return None
        if client is None:
            client = self.client
        return M3U8(client, self.child_urls[index])
    
    def get_ts(self, file_path, decrypt=None, **kwargs):
        """
        get all .ts files and merge them into one
        """
        if not self.is_ts_list:
            print('this is a .m3u8 list')
            return
        assert len(file_path) - file_path.rfind('.ts') == 3
        results = []
        pool = Pool()
        # tqdm progress bar
        bar = tqdm(total=len(self.child_urls))
        bar.set_description('Download & Decrypt')
        update = lambda *args: bar.update()
        # multiprocessing
        for cu in self.child_urls:
            sleep(round(uniform(0, 0.2), 3))    # prevent too frequent requests
            results.append(pool.apply_async(download_ts, (self.client, cu, decrypt), kwargs, callback=update))
        pool.close()
        pool.join()
        # write
        with open(file_path, 'wb') as f:
            for r in results:
                f.write(r.get())    # Process returns ApplyResult
        return
