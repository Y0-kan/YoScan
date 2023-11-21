# -*- coding: utf-8 -*-
'''
1、对子域名结果进行web探活
2、对web探活结果进行指纹识别
'''
from loguru import logger
import os
import datetime
import re
import csv


root = os.getcwd()  # D:\python\YoScan\
pwd = os.path.dirname(os.path.abspath(__file__))  ##D:\python\YoScan\module\tools\

alive_web_url = []  # 存储最终的web探活结果


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


#提取ip并去重
def extract_and_remove_duplicates(ip_list):
    def is_valid_ip(ip):
        ip_pattern = re.compile(
            r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        )
        return re.match(ip_pattern, ip) is not None

    ip_set = set()
    extracted_ips = []  # 用于存储提取的IP数据

    for item in ip_list:
        ip = item.strip()
        if is_valid_ip(ip):
            ip_set.add(ip)  # 将有效的IP添加到集合中

    extracted_ips = list(ip_set)  # 将集合转换为列表

    return extracted_ips

@logger.catch()
def runcmd(toolname,cmd,output_filename):
    '''
    运行各个工具的命令
    '''
    global alive_web_url
    logger.info('-' * 10 + f'start {str(toolname)} ' + '-' * 10)
    logger.info(f"[+] command:{cmd}")
    os.system(cmd)
    if os.path.exists(output_filename):
        with open(output_filename,'r',encoding='utf-8') as f:
            for line in f.readlines():
                alive_web_url.append(line.strip())
        alive_web_url = list(set(alive_web_url))



@logger.catch
def httpx(domain=None,date=None,finger_log_folder=None):
    global alive_web_url
    #subdomains_ips = []

    logger.info('-' * 10 + f'start httpx' + '-' * 10)
    output_filename = f"{finger_log_folder}/{domain}.httpx.csv"
    subdomains = f'result/{date}/{domain}.final.subdomains.txt'
    cmdstr = f'{pwd}/httpx/httpx.exe -l {subdomains} -ip -silent -no-color -csv -o {output_filename}'
    runcmd("httpx", cmdstr, '')

    with open(output_filename, 'r', errors='ignore') as f:
        reader = csv.reader(f)
        head = next(reader)  #使用next函数进行迭代，使得下面的for循环中不包含标题信息
        for row in reader:
            alive_web_url.append(row[8].strip())  # url
            #subdomains_ips.append(row[18].strip())  # host

    #提取ip并去重
    #subdomains_ips = extract_and_remove_duplicates(list(set(subdomains_ips)))



@logger.catch
def httprobe(domain=None,date=None,finger_log_folder=None):
    output_filename = f"{finger_log_folder}\\{domain}.httprobe.txt"
    subdomains = f'result\\{date}\\{domain}.final.subdomains.txt'
    cmdstr = f'type {subdomains} | {pwd}\\httprobe\\httprobe.exe > {output_filename}'
    runcmd("httprobe", cmdstr, output_filename)


@logger.catch
def domain_alive3(domain=None,finger_log_folder=None):
    pass


@logger.catch
def final_subdomain(domain=None,date=None):
    '''
    将最终的web存活探测结果写入到文件中
    '''
    global alive_web_url

    # 将url中，http默认端口80和https默认端口443删掉，避免不同探活工具默认端口显示策略不同 ，造成去重不彻底
    def replace_ports(url):
        pattern = r":(80|443)"
        replacement = ""
        result = re.sub(pattern, replacement, url)
        return result


    for i in range(len(alive_web_url)):
        alive_web_url[i]=replace_ports(alive_web_url[i])

    alive_web_url=list(set(alive_web_url))

    with open(f"result/{date}/{domain}.alive.web.txt", 'w', encoding='utf-8') as f1:
        f1.write("\n".join(map(str,alive_web_url)))
    logger.info(f'[+] Finally, find alive web number: {len(alive_web_url)}')
    logger.info(f'[+] Finally, find alive web outputfile: result/{date}/{domain}.alive.web.txt')


@logger.catch
def ehole(domain=None,date=None,finger_log_folder=None):
    alive_web = f'result/{date}/{domain}.alive.web.txt'
    output_filename = f"{finger_log_folder}\\{domain.replace('.','_')}_ehole.xlsx"  # ehole输出结果中不能有其他'.'
    cmdstr = f'{pwd}/Ehole/ehole.exe finger -l {alive_web} -o {output_filename}'
    runcmd("ehole", cmdstr, '')


@logger.catch
def run(domain=None, date=None, proxy=None):
    #create_logfile()
    #get_system()

    date1 = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    date = date if date else date1

    # 创建存储扫描结果的文件夹
    finger_log_folder = os.path.realpath(root+f"/result/{date}/finger_log")
    if os.path.exists(finger_log_folder) is False:
        os.makedirs(finger_log_folder)

    logger.info('-' * 20 + f'start domain_finger' + '-' * 20)


    #由于经常漏报，所以多用几个工具进行探活，然后合并去重
    httpx(domain,date,finger_log_folder)
    httprobe(domain, date, finger_log_folder)
    final_subdomain(domain, date)

    ehole(domain,date,finger_log_folder)





if __name__=='__main__':
    run()