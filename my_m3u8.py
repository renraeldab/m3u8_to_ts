import requests


class Downloader:
    def __init__(self, headers):
        self.headers = headers
    
    def get(self, url):
        return requests.get(url, headers=self.headers)


class M3U8:
    def __init__(self, dl, url):
        self.dl = dl
        self.url_pre = url[:url.rfind('/')+1]
        self.name = url[url.rfind('/')+1:]
        self.text = str(self.dl.get(url).content, 'UTF-8')
        self.is_ts_list = True
        self.is_encoded = False
        if '#EXT-X-KEY' in self.text:
            self.is_encoded = True
        if '.m3u8' in self.text:
            self.is_ts_list = False
        self.child_urls = []
        for line in self.text.split('\n'):
            if '#EXT' not in line and len(line) > 0:
                if 'http' not in line:
                    self.child_urls.append(self.url_pre + line)
                else:
                    self.child_urls.append(url)
        print(self.child_urls)
    
    def get_m3u8_dict(self):
        if self.is_ts_list:
            print('this is a ts list')
            return None
        m3u8_dict = {}
        for cu in self.child_urls:
            m3u8 = M3U8(self.dl, cu)
            m3u8_dict[m3u8.name] = m3u8
        return m3u8_dict
    
    def get_ts(self, file_path):
        if not self.is_ts_list:
            print('this is a m3u8 list')
            return
        if len (file_path) - file_path.rfind('.ts') != 3:
            print('file path should end with .ts')
            return
        with open(file_path, 'wb') as f:
            for cu in self.child_urls:
                print('downloading ' + cu)
                f.write(self.dl.get(cu).content)
        return


test_url = 'http://1257120875.vod2.myqcloud.com/0ef121cdvodtransgzp1257120875/3055695e5285890780828799271/v.f230.m3u8'
test_m3u8 = M3U8(dl, test_url)
test_m3u8.get_ts('test.ts')
