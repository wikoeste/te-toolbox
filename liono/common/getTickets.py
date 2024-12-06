from liono.common import settings,csvtohtml
from liono.logging import logger
import requests,re,textwrap,threading,os,json
requests.packages.urllib3.disable_warnings()

def noresults():
    settings.filedata["Link"].clear()
    settings.filedata["Description"].clear()
    settings.filedata["DateOpened"].clear()

#Derecated as bugzilla was decommissioned in June 2024
'''
def bugzilla(flag):
    ids, reporturls, summs, dateopened, shrtsums, lastmodified = ([], [], [], [], [], [])
    if flag is True:
        params = {'product':'Escalations','assigned_to': settings.uname, 'status':['new','reopened'], 'api_key': settings.bzKey}
    else:
        params = {'product':'Escalations','assigned_to':'vrt-incoming@sourcefire.com','status':'NEW','api_key': settings.bzKey}
    resp = requests.get(settings.bugzilla, params=params, verify=False)
    if resp.status_code == 200:
        jresp = resp.json()
        logger.log("BZ API success found a total of: {}".format(len(jresp['bugs'])))
        #print("BZ API Search", json.dumps(jresp, indent=2))
        for i in jresp['bugs']:
            if i['is_open'] == True:
                ids.append(str(i['id']))
                sumry = re.sub(r","," ", i['summary'])
                summs.append(sumry)
                datefrmt    = re.sub("T.+","", i['creation_time'])
                dateopened.append(datefrmt)
                reporturls.append('<a href=https://bugzilla.vrt.sourcefire.com/show_bug.cgi?id='+str(i['id'])+' target=_blank>'+str(i['id'])+'</a>')
                lastmodfrmt = re.sub("T|Z", " ", i['last_change_time'])
                lastmodified.append(lastmodfrmt)
        if len(ids) > 0:
            # join all lists to strings on new lines
            urls  = "\n".join(reporturls)
            bugs  = "\n".join(ids)
            dates = "\n".join(dateopened)
            mod   = "\n".join(i for i in lastmodified)
            for x in summs:
                short = textwrap.shorten(x, width=75, placeholder="[...]")
                shrtsums.append(short)
            smry = "\n".join(shrtsums)
            settings.filedata["ID"].append(ids)
            settings.filedata["Link"].append(reporturls)
            settings.filedata["Description"].append(shrtsums)
            settings.filedata["DateOpened"].append(dateopened)
            settings.filedata["LastModified"].append(lastmodified)
        else: #noresults()
            logger.log("No BZ Tickets found")
    else:
        error = ("BZ HTTP API ERROR {}".format(resp.status_code))
        logger.log(error)
'''

def jira(url,flag,pw):
    tix, jid, descs, smrys, created, urls, lastmod = ([], [], [], [], [], [], [])
    jql       = None
    match     = re.findall('j.+?\/', url)
    ticketq   = re.sub('\/', '', str(match))
    headers   = {'Content-type': 'application/json'}
    fields    = "&fields=description,summary,created,assignee,reporter,updated"
    api       = "https://jira.talos.cisco.com/browse/"
    rqurl = "https://jira.talos.cisco.com/rest/api/2/search"
    if flag == True:
        if "umbrella" in ticketq: # get my umbrella jira escalations
            jql   = "?jql=reporter="+settings.uname+" and resolution = Unresolved order by updated DESC"
            rqurl = settings.umbjira
            api   = "https://jira.it.umbrella.com/browse"
        elif "all" in url: # get all my open tickets in talos jira
            jql = "?jql=project in(COG,EERS,WEB,AMPBP,TALOSOPS) and (reporter="+settings.uname+" or assignee="+settings.uname+") and resolution = Unresolved order by updated DESC"
        elif "amp" in ticketq or "amp" in url: # get my amp bp escalations
            jql     = "?jql=project=AMPBP and (reporter="+settings.uname+") and resolution = Unresolved order by updated DESC"
        elif "ops" in ticketq or "ops" in url: # get my talos ops tickets
            jql     = "?jql=project=TALOSOPS and reporter="+settings.uname+" and resolution = Unresolved order by updated DESC"
        elif "ret" in ticketq or "ret" in url: # get my ret-eng/effifcayc escalations
            jql     = "?jql=project=EFFICACY and reporter="+settings.uname+" and resolution = Unresolved order by updated DESC"
            api     = "https://jira-eng-rtp3.cisco.com/"
            rqurl    = settings.engjira
        elif "eers" in url: # get my eers escalations
            jql     = "?jql=project=EERS and reporter="+settings.uname+" and resolution = Unresolved order by updated DESC"
        elif "sjc1" in ticketq or "sjc1" in url:
            jql     = "?jql=project=CLAM and reporter=" + settings.uname + " and resolution = Unresolved order by updated DESC"
        elif "thr" in ticketq or "thr" in url:
            jql     = "?jql=project=THR and reporter=" + settings.uname + " and resolution = Unresolved order by updated DESC"
        else: # get my assigned tickets
            jql     = "?jql=project=COG and assignee in ("+settings.uname+") AND status in (Open, Reopened, 'Pending Reporter', 'COG Investigating', 'Pending 3rd Party') order by updated DESC"
    else: # Get all unaasigined jira tickets in the COG queue/project
        jql = '?jql=project=COG and assignee in (EMPTY) order by updated DESC'
    resp = requests.get(rqurl+jql+fields, headers=headers,auth=(settings.uname,pw), verify=False)
    if resp.status_code == 200:
        jresp = resp.json()
        logger.log("JIRA API JSON Success!")
        #print(json.dumps(jresp, indent=2))
        if len(jresp['issues']) > 0:
            for i in jresp['issues']:
                tix.append(i['key'])
                jid.append(i['id'])
                desc = (i['fields']['description'])
                smry = (i['fields']['summary'])
                # format desc and smry to not have line breaks tabs and spacing
                frmtdesc = re.sub(',',' ', desc)
                frmtdesc = re.sub("r'\s+", ' ', frmtdesc)
                frmtsmry = re.sub(',',' ', smry)
                frmtsmry = re.sub("r'\s+", ' ', frmtsmry)
                descs.append(frmtdesc)
                smrys.append(frmtsmry)
                datefrmt = re.sub("T.+", "", i['fields']['created'])
                created.append(datefrmt)
                lastmodfrmt = re.sub("T|\.\d{3}-\d{4}"," ", i['fields']['updated'])
                lastmod.append(lastmodfrmt)
                urls.append('<a href ='+api+i['key']+' target=_blank>'+i['key']+'</a>')
            #join ticket data for printing
            jids        = "\n".join(i for i in jid)
            ticket      = "\n".join(i for i in tix)
            summarys    = "\n".join(i for i in smrys)
            descripts   = "\n".join(i for i in descs)
            datecreated = "\n".join(i for i in created)
            dateupdated = "\n".join(i for i in lastmod)
            links       = "\n".join(i for i in urls)
            settings.filedata["ID"].append(tix)
            settings.filedata["Link"].append(urls)
            settings.filedata["Description"].append(smrys)
            settings.filedata["DateOpened"].append(created)
            settings.filedata["LastModified"].append(lastmod)
        else:
            results = "No Open Jira COG Tickets"
            logger.log(results)
    else:
        error = ("Jira Talos API HTTP ERROR {}".format(resp.status_code))
        print(error)
        logger.log(error)

def unassigned(pw):
    threads = []
    # clear assigned ticket data from dictionary
    settings.filedata.clear()
    settings.filedata = {"ID":[],"Link": [], "Description": [], "DateOpened": [], "LastModified":[]}
    # Show unassigned tickets in jira, bugzilla
    flag = False
    # Show unassigned tickets in jira, bugzilla, and ace
    #t1 = threading.Thread(target=bugzilla, args=(flag,))
    t2 = threading.Thread(target=jira, args=(settings.talosjira, flag, pw))
    #threads.append(t1)
    threads.append(t2)
    for t in threads:
        t.start()
        try:
            t.join()
        except Exception as e:
            logger.log("Error running thread...{}".format(e))
    if settings.filedata is not None:
        csvtohtml.writedata(flag)
        csvtohtml.htmloutput(settings.unassigned)
        fileExists = os.path.exists(settings.unassigned)
        exists = ("The file, ", settings.unassigned + ",exists: {}".format(fileExists))
        logger.log(exists)
    else:
        err = ("No file data in filedata variables from settings\nOr some other error in csv creation")
        logger.log(err)
    threads.clear()
    settings.filedata.clear()
    settings.filedata = {"ID":[],"Link": [], "Description": [], "DateOpened": [], "LastModified":[]}