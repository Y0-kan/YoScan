# -*- coding: utf-8 -*-
'''
1、github敏感信息(username/password/datebase/access key等)
2、baidu、bing敏感信息(登录、后台、上传等）
3、邮箱
4、web ico ssl证书
'''

from loguru import logger
import os
import fire
import datetime
import subprocess
import shutil
from module.tools.sensitiveinfo_tools.Bing import bing


red = '\033[1;31m'
end = '\033[0m'

root = os.getcwd()  # D:\python\YoScan\
pwd = os.path.dirname(os.path.abspath(__file__))  ##D:\python\YoScan\module\tools\

@logger.catch
def SpiderFromBing(domain=None,sensitiveinfo_log_folder=None):
    '''
    Bing爬虫
    # site:domain inurl:admin inurl:login inurl:system 后台 系统
    '''
    logger.info('-' * 10 + f'start bing spider' + '-' * 10)

    subdomain= []
    link = []
    bingspiber = bing.BingSpider()
    subdomain,link = bingspiber.run_subdomain(domain)

    with open(f"{sensitiveinfo_log_folder}/{domain}.BingSpiber.result.txt", 'w', encoding='utf-8') as f1:
        f1.write("\n".join(map(str,link)))

    logger.info(f'[+] Bing Spider finished,outputfile:{sensitiveinfo_log_folder}/{domain}.BingSpider.result.txt')


@logger.catch
def SpiderFromGoogle(domain=None,sensitiveinfo_log_folder=None):
    '''
    调用pagodo工具进行 google dork搜索
    使用的google dork 语法可以在 YoScan\module\tools\sensitiveinfo_tools\Google\pagodo\my_google_dorks.txt文件中修改：
    '''

    logger.info('-' * 10 + f'start google dork spider' + '-' * 10)
    print(f'{red}tips:被ban了可以更换ip 或者 使用 ctrl+c 跳过google dork搜索{end}')

    output_filename = f"{sensitiveinfo_log_folder}/{domain}.GoogleDork.result.txt"
    #cmdstr = f"python3 {pwd}/sensitiveinfo_tools/Google/pagodo/pagodo.py -d {domain} -g {pwd}/sensitiveinfo_tools/Google/pagodo/google_dorks.txt -l -i 5 -x 10 -p socks5h://127.0.0.1:7890 -s {output_filename}"
    cmdstr = f"python3 {pwd}/sensitiveinfo_tools/Google/pagodo/pagodo.py -d {domain} -g {pwd}/sensitiveinfo_tools/Google/pagodo/google_dorks.txt -l -i 5 -x 10 -s {output_filename}"

    logger.info(f"[+] command:{cmdstr}")

    try:
        os.system(cmdstr)
    except KeyboardInterrupt:
        print(f'{red}Ctrl+C 被按下，跳过google dork搜索{end}')

    log1 = f"{root}/mygooglesearch.py.log"
    log2 = f"{root}/pagodo.py.log"
    if os.path.exists(log1):
        os.remove(log1)
    if os.path.exists(log2):
        os.remove(log2)


    logger.info(f'[+] Google Dork Spider finished,outputfile:{output_filename}')


@logger.catch
def GithubDork(domain=None,sensitiveinfo_log_folder=None):

    logger.info('-' * 10 + f'start github dork spider' + '-' * 10)

    print(f'{red}tips:使用 ctrl+c 跳过github dork搜索{end}')

    output_filename = f"{sensitiveinfo_log_folder}/{domain}.GithubDork.result.txt"

    try:
        with open(output_filename, 'w') as f:
            process = subprocess.Popen(
                [f"{pwd}/sensitiveinfo_tools/Github/gitdorks_go/gitdorks_go.exe", "-gd", f"{pwd}/sensitiveinfo_tools/Github/gitdorks_go/github_dorks.txt", "-nws", "20", "-target", domain, "-tf", f"{pwd}/sensitiveinfo_tools/Github/gitdorks_go/tf.txt",
                 "-ew", "3"], stdout=subprocess.PIPE)
            output, _ = process.communicate()
            f.write(output.decode("utf-8"))
        # 将输出同时打印到cmd中
        print(output.decode("utf-8"))
    except KeyboardInterrupt:
        print(f'{red}Ctrl+C 被按下，跳过github dork搜索{end}')


    logger.info(f'[+] Github Dork Spider finished,outputfile:{output_filename}')


@logger.catch
def EmailAll(domain=None,sensitiveinfo_log_folder=None):
    logger.info('-' * 10 + f'start email collect' + '-' * 10)
    # 创建多个子域名结果输出文件夹
    output_filename = f'{sensitiveinfo_log_folder}/{domain}_EmailAll.json'

    cmdstr = f'python3 {pwd}/sensitiveinfo_tools/emailall/emailall.py --domain {domain} run'
    logger.info(f"[+] command:{cmdstr}")
    os.system(cmdstr)
    # 移动结果文件 \sensitiveinfo\emailall\result\vulweb_com\vulweb.com_All.json
    output_filename_tmp = f"{pwd}/sensitiveinfo_tools/emailall/result/{domain.replace('.', '_')}/{domain}_All.json"
    if os.path.exists(output_filename_tmp):
        shutil.copyfile(output_filename_tmp, output_filename)
    else:
        logger.error(f'[-] emailall not found {output_filename_tmp} ')


@logger.catch
def CertInfo(domain=None,sensitiveinfo_log_folder=None,date=None):
    logger.info('-' * 10 + f'start CertInfo collect' + '-' * 10)
    subdomain_file = f'{root}/result/{date}/{domain}.final.subdomains.txt'
    output_filename = f'{sensitiveinfo_log_folder}/{domain}_CertInfo.csv'
    cmdstr = f'python3 {pwd}/sensitiveinfo_tools/Cert/UrlCrawlCerts.py -d {domain} -sf {subdomain_file} -of {output_filename}'
    logger.info(f"[+] command:{cmdstr}")
    os.system(cmdstr)


@logger.catch
def FaviconInfo(domain=None,sensitiveinfo_log_folder=None,date=None):
    logger.info('-' * 10 + f'start web favicon collect' + '-' * 10)
    alive_web_file = f'{root}/result/{date}/{domain}.alive.web.txt'
    output_filename = f'{sensitiveinfo_log_folder}/{domain}_FaviconInfo.txt'
    cmdstr = f'{pwd}/httpx/httpx.exe -l {alive_web_file} -favicon -no-color -o {output_filename}'
    logger.info(f"[+] command:{cmdstr}")
    os.system(cmdstr)


@logger.catch
def run(domain=None, date=None, proxy=None):

    date1 = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    date = date if date else date1

    # 创建存储扫描结果的文件夹
    sensitiveinfo_log_folder = os.path.realpath(root+f"/result/{date}/sensitiveinfo_log")
    if os.path.exists(sensitiveinfo_log_folder) is False:
        os.makedirs(sensitiveinfo_log_folder)

    logger.info('-' * 20 + f'start sensitiveinfo_scan' + '-' * 20)

    SpiderFromBing(domain,sensitiveinfo_log_folder)
    SpiderFromGoogle(domain,sensitiveinfo_log_folder)
    GithubDork(domain,sensitiveinfo_log_folder)
    EmailAll(domain, sensitiveinfo_log_folder)
    CertInfo(domain, sensitiveinfo_log_folder, date)
    FaviconInfo(domain, sensitiveinfo_log_folder, date)



if __name__=='__main__':
    run()