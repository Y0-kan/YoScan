import socket
import ssl
import threading
import queue
import csv
import argparse


lock=threading.RLock()
q = queue.Queue()


def worker(outputfile):
    while True:
        subdomain= q.get()
        Method='ssl'
        try:
          # 获取ssl证书信息
          ctx = ssl.create_default_context()
          ctx.check_hostname = False
          s = ctx.wrap_socket(socket.socket(), server_hostname=subdomain)
          s.settimeout(3)
          s.connect((subdomain, 443))
          cert = s.getpeercert()
          print(cert['subject'])
          lock.acquire()
          with open(outputfile, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([subdomain, str(cert['subject'])])
          lock.release()
        except ssl.SSLError as e:
          print(f"Failed to get certificate from {subdomain}: {e}")
        except Exception as e:
          print(f"Error:{e}")


        q.task_done()

def cert(domain,subdomainfile,outputfile):
    subdomain_list = []
    with open(subdomainfile, 'r') as f:
        for i in f:
            subdomain_list.append(i.strip())

    with open(outputfile, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['subdomain', 'CertInfo'])

    for _ in range(5):
        t = threading.Thread(target=worker,args=(outputfile,))
        t.daemon = True
        t.start()


    for subdomain in subdomain_list:
        q.put(subdomain)

    q.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain', type=str)
    parser.add_argument('-sf', '--subdomainfile', type=str)
    parser.add_argument('-of', '--outputfile',type=str)
    args = parser.parse_args()
    domain = args.domain
    subdomainfile = args.subdomainfile
    outputfile = args.outputfile
    cert(domain,subdomainfile,outputfile)
