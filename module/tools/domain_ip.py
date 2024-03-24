# -*- coding: utf-8 -*-
'''
1、对子域名结果进行cdn、cloud识别,获取真实ip，以及ip C段整理
2、将真实ip结果进行top1000端口扫描
'''

#serverscan gogo

from loguru import logger
import os
import datetime
import re
import socket
import concurrent.futures


root = os.getcwd()  # D:\python\YoScan\
pwd = os.path.dirname(os.path.abspath(__file__))  ##D:\python\YoScan\module\tools\

nocdn_domain = []   #存储没有使用cdn的域名
real_ip = []  # 存储最终的真实ip结果

# def create_logfile():
#     if os.path.exists(f'{os.getcwd()}/log') is False:
#         os.makedirs(f'{os.getcwd()}/log')
#     logger.add('log/runtime.log',level="INFO",encoding='utf-8')
#     logger.add('log/error.log',level='ERROR',encoding='utf-8')
#
#
# def get_system():
#     platform = sys.platform
#     if platform != 'win32':
#         print("Get system type error. Windows only!!")
#         exit(1)


# 定义DNS查询函数
def dns_lookup(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        print(f'{domain}: {ip_address}')
        return ip_address
    except socket.gaierror:
        print(f'Failed to resolve {domain}')


@logger.catch()
def runcmd(toolname,cmd,output_filename):
    '''
    运行各个工具的命令
    '''
    global nocdn_domain
    logger.info('-' * 10 + f'start {str(toolname)} ' + '-' * 10)
    logger.info(f"[+] command:{cmd}")
    os.system(cmd)
    if os.path.exists(output_filename):
        with open(output_filename,'r',encoding='utf-8') as f:
            for line in f.readlines():
                nocdn_domain.append(line.strip())
        nocdn_domain = list(set(nocdn_domain))
        #print(len(nocdn_domain),nocdn_domain)


@logger.catch()
def eeyes(domain=None,date=None,ip_log_folder=None):
    global nocdn_domain

    #logger.info('-' * 10 + f'start eeyes' + '-' * 10)
    output_filename = f"{ip_log_folder}\\{domain}.eeyes.txt"
    runlog_filename = f"{ip_log_folder}\\{domain}.eeyes.runlog.txt"
    subdomains = f'result\\{date}\\{domain}.final.subdomains.txt'
    cmdstr = f'{pwd}\\Eeyes\\Eeyes.exe -l {subdomains} -log {runlog_filename} > {output_filename}'
    runcmd("eeyes", cmdstr, '')

    #提取 nocdn domain
    with open(runlog_filename,'r',encoding='utf-8') as f:
        for line in f.readlines():
            if "iscdn: false" in line:
                matches = re.findall(r'([a-zA-Z0-9.-]+\.[a-zA-Z]{3,})', line)
                nocdn_domain.append(''.join(matches))


@logger.catch()
def fcdn(domain=None,date=None,ip_log_folder=None):
    output_filename = f"{ip_log_folder}\\{domain}.fcdn.nocdn.txt"
    subdomains = f'result\\{date}\\{domain}.final.subdomains.txt'
    cmdstr = f'python3 {pwd}\\fcdn\\fcdn.py -f {subdomains} -o {output_filename}'
    runcmd("fcdn", cmdstr, output_filename)


@logger.catch()
def DomainToIp(domain,date):
    global nocdn_domain
    global real_ip

    logger.info('-' * 10 + 'start DomainToIp' + '-' * 10)

    with concurrent.futures.ThreadPoolExecutor(10) as executor:
        to_do = []
        # 提交任务到线程池
        for subdomain in nocdn_domain:
            obj = executor.submit(dns_lookup, subdomain)
            to_do.append(obj)
        for future in concurrent.futures.as_completed(to_do):
            real_ip.append(future.result())

    real_ip = list(set(real_ip))
    with open(f"result/{date}/{domain}.nocdn.real_ip.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(map(str, real_ip)))
    logger.info(f'[+] Finally, find real_ip number: {len(real_ip)}')
    logger.info(f'[+] Finally, find real_ip outputfile: result/{date}/{domain}.nocdn.real_ip.txt')
    
    nocdn_domain = [] 
    real_ip = [] 


@logger.catch()
def count_ips_by_c_segment(domain=None, date=None):

    ip_count = {}

    # 读取文件并提取IP地址
    ips = f"result/{date}/{domain}.nocdn.real_ip.txt"

    with open(ips, 'r') as file:
        for line in file:
            ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', line)
            for ip in ips:
                # 提取C段
                c_segment = '.'.join(ip.split('.')[:3])
                # 更新字典中的计数
                if c_segment in ip_count:
                    ip_count[c_segment] += 1
                else:
                    ip_count[c_segment] = 1

    # 打印每个C段的IP数量
    for c_segment, count in ip_count.items():
        print(f'C段: {c_segment}' + '.0/24' + f'     ip数量: {count}')
        with open(f"result/{date}/{domain}.nocdn.real_ip.c_segment.txt",'a', encoding='utf-8') as f:
            f.write(f'C段: {c_segment}' + '.0/24' + f'     ip数量: {count}\n')

    logger.info(f'[+] Finally, find real_ip c_segment outputfile: result/{date}/{domain}.nocdn.real_ip.c_segment.txt')

def TxPortMap(domain=None, date=None):

    logger.info('-' * 10 + f'start real_ip port scan, use TxPortMap' + '-' * 10)

    outputfile = f"result/{date}/{domain}.nocdn.real_ip.top1000.portscan.txt"
    ips = f"result/{date}/{domain}.nocdn.real_ip.txt"

    cmdstr = f'{pwd}/TxPortMap/TxPortMap.exe -t1000 -nbtscan -l {ips} -o {outputfile}'
    #cmdstr = f'{pwd}/TxPortMap/TxPortMap.exe -p 80 -nbtscan -l {ips} -o {outputfile}'
    logger.info(f"[+] command:{cmdstr}")
    os.system(cmdstr)
    logger.info(f'[+] TxPortMap top1000 portscan finished,outputfile:{outputfile}')


@logger.catch
def run(domain=None, date=None, proxy=None):
    #create_logfile()
    #get_system()

    date1 = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    date = date if date else date1

    # 创建存储扫描结果的文件夹
    ip_log_folder = os.path.realpath(root+f"/result/{date}/ip_log")
    if os.path.exists(ip_log_folder) is False:
        os.makedirs(ip_log_folder)

    logger.info('-' * 20 + f'start domain_ip' + '-' * 20)

    eeyes(domain,date,ip_log_folder)
    fcdn(domain, date, ip_log_folder)
    DomainToIp(domain,date)

    count_ips_by_c_segment(domain, date)

    TxPortMap(domain, date)



if __name__=='__main__':
    run()
