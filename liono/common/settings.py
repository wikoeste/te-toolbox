import getpass,re,os.path,queue,datetime
# Global vars inititialized
def init():
    global uname,cec,umb,bzKey,que,umbjira,talosjira,tejira,lastninety,elasticqrys
    global bugzilla,filedata,csvfname,rj,sherlockKey
    global htmlfname,homedir,templatespath,fname,junoKey,juno,que,results,guidconvert
    global acedbhost,acedatabase

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
def getKey(keyname):
    #take the search keyname and return the appropriate api key
    with open(fname, 'r') as fp:
        lines = fp.read().splitlines()
        for l in lines:
            if keyname.upper() in l:
                match = l
    key = re.sub(r'.*=','',match)
    #print(key)
    return key
que = queue.Queue()
cec                 = ''
uname               = getpass.getuser()
fname,homedir       = gethome()
bzKey               = getKey("bz_api")
junoKey             = getKey("jupiter")
sherlockKey         = getKey("sherlock")
#juno                = 'https://prod-juno-search.sv4.ironport.com/'
juno                = 'https://prod-juno-search-api.sv4.ironport.com/'
juno90              = "https://prod-juno-search-api.sco.cisco.com/juno_past_3_months/_search?"
acedbhost           ='ava-tdbro-01prd.vrt.sourcefire.com'
acedatabase         ='analyst_console'
templatespath       ="/Users/wikoeste/PycharmProjects/te1-webapp/templates/"
lastninety          = datetime.datetime.now() - datetime.timedelta(90)
lastseven           = datetime.datetime.now() - datetime.timedelta(7)
# ticket web urls
umbjira             = "https://jira.it.umbrella.com/rest/api/2/search"
talosjira           = "https://jira.talos.cisco.com/rest/api/2/search"
tejira              = "https://jira.sco.cisco.com/rest/api/2/search"
bugzilla            = "https://bugzilla.vrt.sourcefire.com/rest/bug"
ace                 = "https://analyst-console.vrt.sourcefire.com"
# data dictionary of all ticket data
filedata            = {"ID":[],"Link":[],"Description":[],"DateOpened":[],"LastModified":[]}
elasticqrys         = {"cids":[],"cats":[]}
guidconvert         = {"cid":[],"date":"","rj":[],"esascores":[],'corpscores':[],'rjscores':[],'sbrs':[]}
#bzsearchresults    = [{'bugs':'','smry':'','stats':'','opened':'','owner':''}]
bzsearchresults     = {}
sbjatresults        = {"tickets":[],"date":[],"scores":[],"hits":[]}
# file names
csvfname            = os.path.join(templatespath, "casemanager-smry.csv")
htmlfname           = os.path.join(templatespath, "assigned.html")
unassigned          = os.path.join(templatespath, "unassigned.html")
elastichtml         = os.path.join(templatespath, "elasticresults.html")
cmdresultshtml      = os.path.join(templatespath, "guidconvertresults.html")
bzsearchresultshtml = os.path.join(templatespath, "bzsearchresults.html")
rjresultshtml       = os.path.join(templatespath, "rjresults.html")
sbjathtml           = os.path.join(templatespath, "sbjat.html")
acehtml             = os.path.join(templatespath, "acetickets.html")