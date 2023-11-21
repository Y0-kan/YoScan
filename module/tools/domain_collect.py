# -*- coding: utf-8 -*-
'''
多个工具扫描子域名
'''

from loguru import logger
import os
import dns
import sys
import json
import csv
import datetime
import tldextract

red = '\033[1;31m'
end = '\033[0m'

subdomains = []  # 存储最终的子域名结果

root = os.getcwd()  # D:\python\YoScan\
pwd = os.path.dirname(os.path.abspath(__file__))  ##D:\python\YoScan\module\tools\


def create_logfile():
    if os.path.exists(f'{os.getcwd()}/log') is False:
        os.makedirs(f'{os.getcwd()}/log')
    logger.add('log/runtime.log',level="INFO",encoding='utf-8')
    logger.add('log/error.log',level='ERROR',encoding='utf-8')


#判断泛解析
def checkPanAnalysis(domain):
    logger.info('-' * 10 + f'start checkPanAnalysis' + '-' * 10)
    panDomain = 'sadfsadnxzjlkcxjvlkasdfasdf.{}'.format(domain)
    try:
        dns_A_ips = [j for i in dns.resolver.query(panDomain, 'A').response.answer for j in i.items]
        print(dns_A_ips)
        logger.error('[PanAnalysis] {} -> {}'.format(panDomain, dns_A_ips))
        return True
    except Exception as e:
        logger.info('[Not PanAnalysis] :{}'.format(e.args))
        return False


def get_system():
    platform = sys.platform
    if platform != 'win32':
        print("Get system type error. Windows only!!")
        exit(1)


@logger.catch()
def runcmd(toolname,cmd,subdomain_file):
    '''
    运行各个工具的命令
    '''
    global subdomains
    logger.info('-' * 10 + f'run {str(toolname)} ' + '-' * 10)
    if toolname == 'amass' or toolname == 'ksubdomain':
        print(f'{red}tips:使用 ctrl+c 跳过{toolname}扫描{end}')
    logger.info(f"[+] command:{cmd}")
    os.system(cmd)
    if os.path.exists(subdomain_file):
        with open(subdomain_file,'r',encoding='utf-8') as f:
            for line in f.readlines():
                subdomains.append(line.strip())
        subdomains = list(set(subdomains))


@logger.catch
def amass(domain=None,subdomains_log_folder=None):
    global subdomains
    #print(f'{red}tips:使用 ctrl+c 跳过amass扫描{end}')
    output_filename = f"{subdomains_log_folder}/{domain}.amass.json"
    cmdstr = f'{pwd}/amass/amass.exe enum -d {domain} -json {output_filename}'      #调整下参数
    #cmdstr = f'{pwd}/amass/amass.exe enum -active -brute -max-depth 3 -d {domain} -json {output_filename}'
    try:
        runcmd("amass", cmdstr, "")
        # amass输出的是类似下面这种的json文件，需要再提取一下子域名
        # {"name":"crm.xxx.com","domain":"xxx.com","addresses":[{"ip":"","cidr":"","asn":45090,"desc":""}],"tag":"brute","sources":["xx"]}
        with open(output_filename, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                amass_data = json.loads(line.strip())
                if 'name' in amass_data:
                    subdomains.append(amass_data['name'])
        subdomains = list(set(subdomains))
    except KeyboardInterrupt:
        print(f'{red}Ctrl+C 被按下，跳过amass扫描{end}')


@logger.catch
def ksubdomain(domain=None,subdomains_log_folder=None):
    output_filename = f"{subdomains_log_folder}\\{domain}.ksubdomain.txt"
    cmdstr = f'{pwd}/ksubdomain/ksubdomain.exe enum --band 5M --domain {domain} --silent --only-domain --skip-wild --level 2 --output {output_filename}'
    #print(f'{red}tips:使用 ctrl+c 跳过ksubdomain扫描{end}')
    try:
        runcmd("ksubdomain",cmdstr,output_filename)
    except KeyboardInterrupt:
        print(f'{red}Ctrl+C 被按下，跳过ksubdomain扫描{end}')

    temp_file = f'{root}/ksubdomain.yaml'
    if os.path.exists(temp_file) is True:
        os.remove(temp_file)


@logger.catch
def subfinder(domain=None,subdomains_log_folder=None):
    output_filename = f"{subdomains_log_folder}/{domain}.subfinder.txt"
    cmdstr = f'{pwd}/subfinder/subfinder.exe -d {domain} -all -no-color -o {output_filename}'
    runcmd("subfinder", cmdstr, output_filename)


@logger.catch
def ctfr(domain=None,subdomains_lost_folder=None):
    output_filename = f"{subdomains_lost_folder}/{domain}.ctfr.txt"
    cmdstr = f"python3 {pwd}/ctfr/ctfr.py  --domain {domain} --output {output_filename}"
    runcmd("ctfr", cmdstr, output_filename)


@logger.catch
def oneforall(domain=None,subdomains_log_folder=None):
    '''
    ToDo：后面对一些工具使用子进程的方式执行，便于设置超时以及kill相应程序
    '''
    global subdomains
    output_filename = f"{subdomains_log_folder}/{domain}.oneforall.csv"
    cmdstr = f"python3 {pwd}/OneForAll/oneforall.py --target {domain} --path {output_filename} run"
    runcmd("oneforall", cmdstr, "")
    if os.path.exists(output_filename):
        with open(output_filename, 'r') as f:
            reader = csv.reader(f)
            head = next(reader)  #使用next函数进行迭代，使得下面的for循环中不包含标题信息
            for row in reader:
                subdomains.append(row[5])
    subdomains = list(set(subdomains))


@logger.catch
def final_subdomain(domain=None,date=None):
    '''
    1、将最终的子域名扫描结果写入到文件中；
    2、结果中可能有其他主域，分离出来，写入另一个文件
    '''
    global subdomains
    other_subdomains_list = []
    for subdomain in subdomains:
        # 解析结果中的域名，判断是否与输入的域名相同，然后存储到不同位置
        parse_domain = tldextract.extract(subdomain)
        if domain != parse_domain.domain + '.' + parse_domain.suffix:
            other_subdomains_list.append(subdomain)
            subdomains.remove(subdomain)
    with open(f"result/{date}/{domain}.final.subdomains.txt", 'w', encoding='utf-8') as f1:
        f1.write("\n".join(map(str,subdomains)))
    with open(f"result/{date}/{domain}.other.subdomains.txt", 'w', encoding='utf-8') as f2:
        f2.write("\n".join(map(str,other_subdomains_list)))
    logger.info(f'[+] Finally, find subdomains number: {len(subdomains)}')
    logger.info(f'[+] Finally, find subdomains outputfile: result/{date}/{domain}.final.subdomains.txt')


@logger.catch
def run(domain=None, date=None, proxy=None):
    create_logfile()
    get_system()

    date1 = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    date = date if date else date1

    # 创建存储扫描结果的文件夹
    subdomains_log_folder = os.path.realpath(root+f"/result/{date}/domain_log")
    if os.path.exists(subdomains_log_folder) is False:
        os.makedirs(subdomains_log_folder)

    logger.info('-' * 20 + f'start domain_scan' + '-' * 20)

    if checkPanAnalysis(domain) is False:
        #progress_record   todo:记录一下进度？
        amass(domain,subdomains_log_folder)
        ksubdomain(domain,subdomains_log_folder)
        subfinder(domain,subdomains_log_folder)
        ctfr(domain,subdomains_log_folder)
        oneforall(domain,subdomains_log_folder)
        final_subdomain(domain,date)
    else:
        logger.error(f"{domain} exists pan analysis, stop scanning")



if __name__=='__main__':
    run()