import requests
from urllib.parse import quote, urlparse
import threading
from bs4 import BeautifulSoup
import random
import time


USERAGENT = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]


# 必应爬虫
class BingSpider:
    def __init__(self):
        # site:domain inurl:admin inurl:login inurl:system 后台 系统
        self.wds = ['admin', 'login', 'system', 'register', 'upload', '后台', '系统', '登录','管理']
        self.PAGES = 5   # 默认跑5页
        # print('Please wait a few time ...')
        self.TIMEOUT = 10
        self.bingSubdomains = []
        self.links = []
    def get_subdomain(self, host, each_wd):      # host 既可以是域名也可以是IP
        for page in range(1, self.PAGES + 1):
            q = 'site:{} {}'.format(host, each_wd)
            print('[{}] -> [page: {}]'.format(q, page))
            tmp = page - 2
            if tmp == -1:
                first_value = 1
            elif tmp == 0:
                first_value = 2
            else:
                first_value = tmp * 10 + 2
            url = r'https://www.bing.com/search?q={}&first={}'.format(quote(q), first_value)
            print(url)
            ua = random.choice(USERAGENT)
            headers = {
                'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                'Cache-Control': 'max-age=0',
                'DNT': '1',
                'Referer': 'https://www.bing.com/',
                'User-Agent': ua
            }
            try:
                res = requests.get(url=url, headers=headers, timeout=10)
                #print(res.text)
                soup = BeautifulSoup(res.text, 'html.parser')
                lis = soup.find_all('li', class_='b_algo')
                #print(lis)
                for li in lis:
                    li_a = li.find('a')
                    link = li_a['href']                      # 链接
                    title = li_a.get_text()                  # 标题
                    subdomain = urlparse(link).netloc         # 子域名
                    print('[{}] [page: {}]: {} {} {}'.format(q, page, link, title, subdomain))
                    self.bingSubdomains.append(subdomain)
                    self.links.append([each_wd, link])
            except Exception as e:
                print(e.args)
                # pass
    # 爬子域名
    def run_subdomain(self, domain):
        # threads = []
        # for i in range(len(self.wds)):
        #     t = threading.Thread(target=self.get_subdomain, args=(domain, self.wds[i]))
        #     threads.append(t)
        #     t.start()
        # for t in threads:
        #     t.join()
        for i in range(len(self.wds)):
            self.get_subdomain(domain, self.wds[i])
            time.sleep(3)


        return list(set(self.bingSubdomains)), self.links

if __name__ == '__main__':
    subdomain= []
    link = []
    bing = BingSpider()
    subdomain,link = bing.run_subdomain('test.com')

    print(len(link),link)