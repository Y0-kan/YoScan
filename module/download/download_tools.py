import os
import sys
import yaml
import time
import requests
import zipfile
import tarfile
import shutil
import patoolib
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, ALL_COMPLETED, wait, as_completed

def get_system():
    platform = sys.platform
    if platform == 'win32':
        return "windows"
    else:
        print("sorry, only windows now")
        exit(1)


class Download:
    def __init__(self,proxy=None):
        # logger.info('检查是否已安装工具，如缺少将进行安装
        self.download_path = 'download_tmp'
        self.proxy = proxy
        self.tools_dict = {}
        self.rootpath = os.getcwd()
        self.pwd = os.path.dirname(os.path.abspath(__file__))
        self.suffix = ".exe"
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.tools_installed = {}
        self.getconfig()

        if os.path.exists(self.download_path) is False:
            os.makedirs(self.download_path)
        for k in self.tools_dict.keys():
            if self.tools_dict[k]['whetherdownload'] is True:
                self.tools_installed[k] = False

    def getconfig(self):
        toolsyaml_path = f"{self.pwd}/tools.yml"
        if os.path.exists(toolsyaml_path):
            with open(toolsyaml_path) as f:
                self.tools_dict = yaml.load(f,Loader=yaml.FullLoader)
                #print(self.tools_dict)
        else:
            logger.error(f"[-] not found {toolsyaml_path}")
            logger.error("Exit!")
            exit(1)

    def unzipfile(self,filename,dirs="."):
        if os.path.exists(dirs) is False:
            os.makedirs(dirs)

        try:
            if os.path.splitext(filename)[1] in ["", ".exe", ".db"]:
                shutil.copy(filename, dirs)
                logger.info(f"[+] move {filename} success")
            else:
                patoolib.extract_archive(filename, outdir=dirs)
                logger.info(f"[+] unzip {filename} success")
        except:
            logger.error(f"[-] unzip {filename} to {dirs}failed.")

        # if zipfile.is_zipfile(filename):
        #     zf = zipfile.ZipFile(filename,'r')
        #     zf.extractall(path=dirs)
        #     zf.close()
        #     logger.info(f"[+] unzip {filename} success")
        # elif tarfile.is_tarfile(filename):
        #     tf = tarfile.open(filename)
        #     tf.extractall(path=dirs)
        #     tf.close()
        # elif os.path.splitext(filename)[1] in ["", ".exe", ".db", ".7z"]:
        #     shutil.copy(filename, dirs)
        # else:
        #     logger.error(f"[-] unzip {filename} to {dirs}failed.")
        #     return



    def downloadfile(self,url,dst_file,dst_path='download'):
        target_filename = f'{dst_path}/{dst_file}'
        if os.path.exists(target_filename) is False:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}
                proxies = {
                    'http': self.proxy,
                    'https': self.proxy
                }
                response = requests.get(url,headers=headers,proxies=proxies,stream=True)
                with open(target_filename,"wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                logger.info(f"[+] Download {dst_file} success.")
                return target_filename
            except Exception as e:
                logger.error(e)
                logger.error(f"[-] Download {dst_file} fail!")
                return False

    def handle(self,toolinfo):
        installflag = False
        try:
            if toolinfo['whetherdownload']:
                # 判断工具是否已经存在对应目录，不存在则下载,如果有则不再下载解压和重命名
                tool_filename = f"{toolinfo['topath'][0]}/{toolinfo['final_name']}"
                if os.path.exists(tool_filename) is False:
                    installflag = True
                else:
                    if os.path.isdir(tool_filename):
                        tool_filename = f"{toolinfo['topath'][0]}/{toolinfo['final_name']}/{toolinfo['tool_main_filename']}"
                        if os.path.exists(tool_filename) is False:
                            installflag = True
                            shutil.rmtree(f"{toolinfo['topath'][0]}/{toolinfo['final_name']}")  # 如果存在则删除文件夹,否则不能rename
                        else:
                            installflag = False
                    else:
                        installflag = False
                if installflag is True:
                    zip_path = self.downloadfile(url=toolinfo['link'],dst_file=toolinfo['downloadfile'],dst_path=self.download_path)
                    time.sleep(2)
                    if zip_path:
                        self.unzipfile(filename=zip_path, dirs=toolinfo['topath'][0])
                        time.sleep(2)
                        if toolinfo['source_name'] != toolinfo['final_name']:
                            os.rename(f"{os.getcwd()}/{toolinfo['topath'][0]}/{toolinfo['source_name']}",
                                      f"{os.getcwd()}/{toolinfo['topath'][0]}/{toolinfo['final_name']}")
                        self.tools_installed[toolinfo['toolname']] = True
                else:
                    self.tools_installed[toolinfo['toolname']] = True
                    logger.info(f"[*] {tool_filename} already exists. Skip download and unzip.")
        except:
            return False

    def run(self):
        flag = 0
        all_task = [self.executor.submit(self.handle, tinfo) for tinfo in self.tools_dict.values()]
        for future in as_completed(all_task):
            try:
                result = future.result()
            except Exception as e:
                logger.exception(f"ThreadPoolExecutor:\n{e}")
                print(e)

        # 检查是否所有tools安装好了，否则退出
        for k, v in self.tools_installed.items():
            if v is False:
                logger.error(f"[-] {k} install failed")
                flag += 1
        shutil.rmtree(f"{self.download_path}")
        if flag != 0:
            logger.error(f"[-] Please install tools that are not installed before using")
            exit()
        else:
            logger.info(f"\n[+] All tools are installed\n")


if __name__ == '__main__':
    dd = Download()
    dd.run()