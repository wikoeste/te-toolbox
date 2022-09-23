from liono.common import settings
from liono.common import csvtohtml
import requests,json,re,textwrap,datetime,threading,csv,os
requests.packages.urllib3.disable_warnings()
from terminaltables import AsciiTable, SingleTable
from jira import JIRA

def noresults():
    settings.filedata["Link"].clear()
    settings.filedata["Description"].clear()
    settings.filedata["DateOpened"].clear()

def bugzilla(flag,q):
    ids, reporturls, summs, dateopened, shrtsums, lastmodified = ([], [], [], [], [], [])
    if flag is True:
        params = {'product':'Escalations','assigned_to': settings.uname, 'status':['new','reopened'], 'api_key': settings.bzKey}
    else:
        params = {'product':'Escalations','assigned_to':'vrt-incoming@sourcefire.com','status':'NEW','api_key': settings.bzKey}
    resp = requests.get(settings.bugzilla, params=params, verify=False)
    if resp.status_code == 200:
        jresp = resp.json()
        #print("BZ API Search", json.dumps(jresp, indent=2))
        for i in jresp['bugs']:
            if i['is_open'] == True:
                ids.append(str(i['id']))
                summs.append(i['summary'])
                dateopened.append((i['creation_time']))
                reporturls.append('<a href=https://bugzilla.vrt.sourcefire.com/show_bug.cgi?id='+str(i['id'])+' target=_blank>'+str(i['id'])+'</a>')
                lastmodified.append(i['last_change_time'])
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
                # configure BZ Search tables
                data = [
                    ["ID","BZ-Link","Summary","Date Created","Last Modified"],
                    [bugs,urls,smry,dates,mod],
                ]
            bzResults = AsciiTable(data, "Bugzilla Case Search Results")
            q.put(bzResults)  # put result in que for printing
            settings.filedata["ID"].append(ids)
            settings.filedata["Link"].append(reporturls)
            settings.filedata["Description"].append(shrtsums)
            settings.filedata["DateOpened"].append(dateopened)
            settings.filedata["LastModified"].append(lastmodified)
        else:
            bzResults = AsciiTable([["No Open Tickets"]], "Bugzilla Case Search Results")
            q.put(bzResults)  # put result in que for printing
            #noresults()
        print(bzResults.table)
    else:
        error = ("BZ HTTP API ERROR {}".format(resp.status_code))
        data = [["Bugzilla Tickets", "Error"],["None Found", error]]
        bzResults = AsciiTable(data, "Bugzilla Ticket Search")
        q.put(bzResults)  # put result in que for printing
        #noresults()
        print(bzResults.table)

def jira(url,flag,pw,q):
    jql       = None
    match     = re.findall('j.+?\/', url)
    ticketq   = re.sub('\/', '', str(match))
    #jql      = "?jql=assignee = "+ settings.uname + " and resolution = Unresolved order by updated DESC"
    headers  = {'Content-type': 'application/json'}
    fields   = "&fields=description,summary,created,assignee,reporter,updated"
    tix,jid,descs,smrys,created,urls,lastmod = ([],[],[],[],[],[],[])
    if flag == True:
        if "umbrella" in ticketq:
            jql = "?jql=reporter="+settings.uname+" and resolution = Unresolved order by updated DESC"
            api = "https://jira.it.umbrella.com/browse/"
        elif "talos" in ticketq:
            jql = "?jql=reporter="+settings.uname+" and resolution = Unresolved order by updated DESC"
            api = "https://jira.talos.cisco.com/browse/"
        else:
            jql = '?jql=assignee='+settings.uname+' AND statusCategory not in (Done)'
            api = "https://jira.sco.cisco.com/browse/"
    else:
        jql = '?jql=project=COG and assignee in (EMPTY)'
        api = "https://jira.sco.cisco.com/browse/"
    resp = requests.get(url+jql+fields, headers=headers,auth=(settings.uname,pw), verify=False)
    if resp.status_code == 200:
        jresp = resp.json()
        #print(url, json.dumps(jresp, indent=2))
        if len(jresp['issues']) > 0:
            for i in jresp['issues']:
                tix.append(i['key'])
                jid.append(i['id'])
                desc = (i['fields']['description'])
                smry = (i['fields']['summary'])
                # format desc and smry to not have line breaks tabs and spacing
                frmtdesc = desc.translate(str.maketrans(' ', ' ', '\n\t\r'))
                frmtsmry = smry.translate(str.maketrans(' ', ' ', '\n\t\r'))
                descs.append(frmtdesc)
                smrys.append(frmtsmry)
                created.append(i['fields']['created'])
                lastmod.append(i['fields']['updated'])
                #urls.append(api+i['key'])
                urls.append('<a href ='+api+i['key']+' target=_blank>'+i['key']+'</a>')
            #join ticket data for printing
            jids        = "\n".join(i for i in jid)
            ticket      = "\n".join(i for i in tix)
            summarys    = "\n".join(i for i in smrys)
            descripts   = "\n".join(i for i in descs)
            datecreated = "\n".join(i for i in created)
            dateupdated = "\n".join(i for i in lastmod)
            links       = "\n".join(i for i in urls)
            data = [
                ["Ticket","Summary","Date Opened","Last Updated"],
                [links,summarys,datecreated,dateupdated],
            ]
            results = AsciiTable(data, ticketq)
            settings.filedata["ID"].append(tix)
            settings.filedata["Link"].append(urls)
            settings.filedata["Description"].append(smrys)
            settings.filedata["DateOpened"].append(created)
            settings.filedata["LastModified"].append(lastmod)
        else:
            data = [[url,"No Open Tickets"]]
            results = AsciiTable(data, ticketq)
    else:
        error = ("HTTP ERROR {}".format(resp.status_code))
        data = [[url,error]]
        results = AsciiTable(data, ticketq)
    q.put(results)

def analystconsole(flag,q):
    aceurl = "https://analyst-console.vrt.sourcefire.com/escalations/webrep/disputes?f=wikoeste"
    resp = requests.get(aceurl, verify=False)
    if resp.status_code == 200:
        jresp = resp.json()
        print(json.dumps(jresp, indent=2))
        data = ''
        results = AsciiTable(data, "Analyst Console Tickets: "+ settings.uname)
        '''
        settings.filedata["ID"].append()
        settings.filedata["DateOpened"].append()
        settings.filedata["Link"].append()
        settings.filedata["Description"].append()
        '''
    else:
        error = ("ACE HTTP API ERROR {}".format(resp.status_code))
        data = [[error]]
        results = AsciiTable(data, "ACE Tickets")
    q.put(results)

def unassigned():
    threads = []
    # clear assigned ticket data from dictionary
    settings.filedata.clear()
    settings.filedata = {"ID":[],"Link": [], "Description": [], "DateOpened": [], "LastModified":[]}
    # Show unassigned tickets in jira, bugzilla, and ace
    flag = False
    # Show unassigned tickets in jira, bugzilla, and ace
    t1 = threading.Thread(target=bugzilla, args=(flag,settings.que,))
    t2 = threading.Thread(target=jira, args=(settings.tejira, flag, settings.cec, settings.que))
    # t3 = threading.Thread(target=analystconsole, args=(settings.que, ))
    threads.append(t1)
    threads.append(t2)
    # threads.append(t3)
    for t in threads:
        t.start()
        try:
            t.join()
        except Exception as e:
            print("Error running thread...{}".format(e))
    if settings.filedata is not None:
        csvtohtml.writedata(flag)
        csvtohtml.htmloutput(settings.unassigned)
        fileExists = os.path.exists(settings.unassigned)
        print("The file, ", settings.unassigned + ",exists: {}".format(fileExists))
    else:
        print("No file data in filedata variables from settings")
        print("Or some other error in csv creation")
    threads.clear()
    settings.filedata.clear()
    settings.filedata = {"ID":[],"Link": [], "Description": [], "DateOpened": [], "LastModified":[]}