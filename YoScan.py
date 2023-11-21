# -*- coding: utf-8 -*-
import fire
import datetime
import hashlib
import os
from loguru import logger
from module.download import download_tools
from module.tools import domain_collect
from module.tools import domain_finger
from module.tools import domain_ip
from module.tools import sensitiveinfo_scan


yellow = '\033[01;33m'
white = '\033[01;37m'
green = '\033[01;32m'
blue = '\033[01;34m'
red = '\033[1;31m'
end = '\033[0m'

version = 'v1.0'
message = white + '{' + red + version + white + '}'

YoScan_banner = f"""
{red}YoScan is a comprehensive asset collection tool{red}                                                     
                        .--.--.                                       
        ,---,          /  /    '.                                       {message}{green}
       /_ ./|   ,---. |  :  /`. /                              ,---,    {green}
 ,---, |  ' :  '   ,'\;  |  |--`                           ,-+-. /  |   {green}
/___/ \.  : | /   /   |  :  ;_       ,---.     ,--.--.    ,--.'|'   |   {yellow}
 .  \  \ ,' '.   ; ,. :\  \    `.   /     \   /       \  |   |  ,"' |   {yellow}
  \  ;  `  ,''   | |: : `----.   \ /    / '  .--.  .-. | |   | /  | |   {yellow}
   \  \    ' '   | .; : __ \  \  |.    ' /    \__\/: . . |   | |  | |   {blue}
    '  \   | |   :    |/  /`--'  /'   ; :__   ," .--.; | |   | |  |/    {blue}
     \  ;  ;  \   \  /'--'.     / '   | '.'| /  /  ,.  | |   | |--'     {blue}
      :  \  \  `----'   `--'---'  |   :    :;  :   .'   \|   |/         {red}
       \  ' ;                      \   \  / |  ,     .-./'---'          {red}
        `--`                        `----'   `--`---'                   {red} 
{end}
"""

#print(YoScan_banner)

class YoScan(object):
    '''
    YoScan is a comprehensive asset collection tool

    mode:
        install     Download the required tools
        run         subdomian, survival detection, finger, ip, sensitive information

    example:
        python3 YoScan.py install
        python3 YoScan.py --proxy socks5://127.0.0.1:7890 install
        python3 YoScan.py --domain example.com run
        python3 YoScan.py --domains ./domains.txt run

    '''

    def __init__(self,domain=None, domains=None,date=None,proxy=None):
        self.domain = domain
        self.domains = domains
        self.proxy = proxy
        self.domains_list = []
        date1 = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        self.date = date if date else date1

        print(YoScan_banner)
        #self.randomstr = hashlib.md5(bytes(self.date, encoding='utf-8')).hexdigest()

        if self.domain or self.domains:
            # 创建结果文件夹
            self.result_folder = f"result/{self.date}"
            if os.path.exists(self.result_folder) is False:
                os.makedirs(self.result_folder)

        #处理单域名和多域名
        if self.domain and self.domains is None:
            self.domains_list.append(self.domain)
        elif self.domains and self.domain is None:
            with open(self.domains, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    line = line.strip()
                    self.domains_list.append(line)
            self.domains_list = list(set(self.domains_list))  #去重
        else:
            pass
            #print("params error!")
            #exit()

        # 变成绝对路径
        if self.domains is not None:
            if os.path.isabs(self.domains) is False:
                newpath = os.path.realpath(os.getcwd() + '/' + self.domains)
                if os.path.exists(newpath):
                    self.domains = newpath


    def install(self):
        # download tools
        dd = download_tools.Download(proxy=self.proxy)
        dd.run()


    def run(self):
        """
        python3 YoScan.py --domain example.com run
        python3 YoScan.py --domains ./domains.txt run
        """
        if self.domains_list:
            for domain in self.domains_list:
                domain_collect.run(domain=domain, date=self.date, proxy=self.proxy)
                domain_finger.run(domain=domain, date=self.date, proxy=self.proxy)
                domain_ip.run(domain=domain, date=self.date, proxy=self.proxy)
                sensitiveinfo_scan.run(domain=domain, date=self.date, proxy=self.proxy)
        else:
            logger.error("[!] Cann't find any domain. Check your input.")


if __name__ == '__main__':
    fire.Fire(YoScan)
    #dd = download_tools.Download("socks5://127.0.0.1:7890")
    #dd.run()
