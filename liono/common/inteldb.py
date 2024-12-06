from liono.common import settings
import re,requests,time,os
from concurrent.futures import ThreadPoolExecutor
global feeds,url,urls

feeds   = ["hermes.botnet.ipv4.txt", "hermes.kaspersky.ipv4.txt",
        "hermes.malware.ipv4.txt",
        "hermes.phishing.ipv4.txt","zeus.botnet.domains.txt","zeus.botnet.urls.txt",
        "zeus.cncpo.domains.txt","zeus.cncpo.urls.txt","zeus.ctiru.domains.txt",
        "zeus.ctiru.urls.txt","zeus.iwf.domains.txt","zeus.iwf.urls.txt",
        "zeus.kaspersky.domains.txt","zeus.kaspersky.urls.txt",
        "zeus.malware.domains.txt","zeus.malware.urls.txt",
        "zeus.phishing.domains.txt","zeus.phishing.urls.txt"]
url     = "https://feeds-proxy.prod.reseng.umbrella.com/actionman/export-proxy-2/curlink/"
urls	= []

def proxySearch(sample):
    count = 0
    for f in feeds:
        #WORKING SINGLE FEED BY FEED SEARCH
        r = requests.get(url+f)
        if r.status_code == 200:
            if sample in r.text:
                with open(f, 'wb') as fo:
                    fo.write(r.content)
                fo.close
                searchfile = open(f, 'r')
                for line in searchfile:
                    if sample in line:
                        match = line.strip()
                        match = match.strip("\n")
                        settings.inteldbmatches['url'].append(str(match))
                        if f not in settings.inteldbmatches['feed']:
                            settings.inteldbmatches['feed'].append(str(f))
                os.remove(f) # remove/delete the feed text file
                if len(settings.inteldbmatches) > 0:
                    for i in settings.inteldbmatches['url']:
                        count+=1
                    for f in settings.inteldbmatches['feed']:
                        print("Match found in {}".format(f))
                    if count <= 10:
                        for u in settings.inteldbmatches["url"]:
                            print(u)
                    else:
                        print("Total URLS: "+ str(count))
            else:
                print("No match found in {}".format(f))
        else:
            print("Err HTTP".format(r.status_code))

def threader(url,sample):
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        if sample in r.text:
            return url

def lookup(sample):
    settings.inteldbmatches.clear()
    settings.inteldbmatches = {'url': [], 'feed': []}
    for f in feeds:
        urls.append(url+f)
    print("===Umbrella Intelligent Proxy Checker===")
    sample = sample.strip()
    proxySearch(sample)