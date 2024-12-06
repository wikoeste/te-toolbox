import getpass,re,os.path,datetime

# Global vars inititialized
def init():
    global uname,cec,umb,umbjira,talosjira,lastninety,elasticqrys
    global filedata,csvfname,rj,sherlockKey,inteldbmatches
    global htmlfname,homedir,templatespath,fname,junoKey,juno,que,results,guidconvert
    global acedbhost,acedatabase,jkey
    global rule,vrt,snortversion,unedited,projDir,pcapDir,rulesDir

# get home dir location based on OS/platform
def gethome():
    match     = ''
    freebsd   = "/home/{}".format(uname)+"/.profile"
    osx       = "/Users/{}".format(uname)+"/.profile"
    if os.path.exists(freebsd):
        fname   = freebsd
        home    = "/home/{}".format(uname)
    else:
        fname   = osx
        home    = "/Users/{}".format(uname)
    return fname,home

#Get api keys for internal lookups
def getKey(keyname):
    #take the search keyname and return the appropriate api key
    with open(fname, 'r') as fp:
        lines = fp.read().splitlines()
        for l in lines:
            if keyname.upper() in l:
                match = l
    key = re.sub(r'.*=','',match) # remove key name and = sign
    key = re.sub(r'"','',key) # remove quotes from keys
    #print(key)
    return key

# Setting global vars
cec                 = ''
uname               = getpass.getuser()
fname,homedir       = gethome()
junoKey             = getKey("jupiter")
sherlockKey         = getKey("sherlock")
jkey                = getKey("jira")
juno                = 'https://prod-juno-search-api.sv4.ironport.com/'
juno90              = "https://prod-juno-search-api.sco.cisco.com/juno_past_3_months/_search?"
#AnalystConsole Creds
acedbhost           = 'ava-tdbro-01prd.vrt.sourcefire.com'
acedatabase         = 'analyst_console'
templatespath       = "/Users/wikoeste/PycharmProjects/te1-webapp/templates/"
lastninety          = datetime.datetime.now() - datetime.timedelta(90)
lastseven           = datetime.datetime.now() - datetime.timedelta(7)
# ticket web urls
umbjira             = "https://jira.it.umbrella.com/rest/api/2/search"
talosjira           = "https://jira.talos.cisco.com/rest/api/2/search"
ace                 = "https://analyst-console.vrt.sourcefire.com"
engjira             = "https://jira-eng-rtp3.cisco.com/rest/api/2/search"
clamavjira          = "https://jira-eng-sjc1.cisco.com/rest/api/2/search"
# data dictionary of all ticket data
filedata            = {"ID":[],"Link":[],"Description":[],"DateOpened":[],"LastModified":[]}
elasticqrys         = {"cids":[],"cats":[]}
guidconvert         = {"cid":[],"date":"","rj":[],"esascores":[],'corpscores':[],'rjscores':[],'sbrs':[]}
sbjatresults        = {"tickets":[],"scores":[],"hits":[]}
inteldbmatches      = {'url':[],'feed':[]}

# file names
csvfname            = os.path.join(templatespath, "casemanager-smry.csv")
htmlfname           = os.path.join(templatespath, "assigned.html")
unassigned          = os.path.join(templatespath, "unassigned.html")
elastichtml         = os.path.join(templatespath, "elasticresults.html")
cmdresultshtml      = os.path.join(templatespath, "guidconvertresults.html")
rjresultshtml       = os.path.join(templatespath, "rjresults.html")
acehtml             = os.path.join(templatespath, "acetickets.html")
backlogbuddy        = os.path.join(templatespath, "backlogbuddy.html")

#snort replay
snortversion = ""
rule         = None
unedited     = None
vrt          = None
projDir      = "/Users/" + uname + "/PycharmProjects/te1-webapp/liono/"
pcapDir      = "/Users/" + uname + "/PycharmProjects/te1-webapp/liono/pigreplay/pcaps/"
rulesDir     = "/Users/" + uname + "/PycharmProjects/te1-webapp/liono/pigreplay/snort-rules/"