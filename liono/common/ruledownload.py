from liono.common import settings
import time,requests,re,os,threading,os.path,tarfile

# Downloads snort rules
def getrulefiles():
    #S2 repo NOT used!
    #rulerepo = 'https://repo.vrt.sourcefire.com/svn/rules/trunk/snort-rules/'   # s2 repo
    #####################
    rulerepo = 'https://repo.vrt.sourcefire.com/svn/rules/trunk/snort3/rules/'  # s3 repo
    rulefile = "rules.txt"
    urls, uniqurls = ([], [])
    r = requests.get(rulerepo, auth=(settings.uname, settings.vrt),verify=False, stream=True)
    if r.status_code == 200:
        with open(rulefile, "w") as f:
            f.write(r.text)
        with open(rulefile, 'r+') as f:
            text = f.read().replace(' ', '')
            text = re.sub('<.+">|</a></li>', '', text)
            text = re.sub('<.+|\.\.|.stub.rules|VRT.+.txt', '', text)
            f.seek(0)
            f.write(text)
            f.truncate()
        with open(rulefile) as f:
            for line in f:
                urls.append(rulerepo + line)
        urls = [i.strip('\n') for i in urls]
        [uniqurls.append(n) for n in urls if n not in uniqurls]
        del uniqurls[0]
        f.close
        os.remove(rulefile)
        # download each .rules file into snort-rules
        # multi process/thread the files downloads to save time
        for i in range(len(uniqurls)):
            t1 = threading.Thread(target=ruleloop, args=[uniqurls[i]])
            t1.start()
    else:
        print("HTTP ERROR:", r.status_code)

# check if we need to download the snort rules
def checkrules():
    if os.path.exists(settings.rulesDir) is False:                      # if no snort-rules in user home dir download the rules
        os.makedirs(settings.rulesDir)
        getrulefiles()
    elif os.path.exists(settings.rulesDir+"s3.rules") is True:       # if true snort-rules but timestamp is older than 24 hours, download new rules
        lastmodtime = os.stat(settings.rulesDir+'s3.rules').st_mtime
        now = time.time()
        timediff = int(now) - int(lastmodtime)
        if timediff >= 86400:
            print("Rule file download in process.....\n\n")
            getrulefiles()
            print("Rule Download Successful")
            return True
        else:
            print("No rule download needed as last download was 24 hours ago.")
            return False
    else:                                                               # unknown error so just make snort-rules and download rules
        getrulefiles()
        print("Rule Download Successful")
        return True

# Used to download iterations of multiple rule files call from getrulefiles function
def ruleloop(file):
    name    = file.rsplit('/',1)[-1]
    fname 	= os.path.join(settings.rulesDir,name)
    r    	= requests.get(file, auth=(settings.uname,settings.vrt),verify=False, stream=True)
    with open(fname, 'wb') as f:
        f.write(r.content)
        f.close()