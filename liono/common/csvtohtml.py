from liono.common import settings
import csv,itertools,time

def writedata(flag):
    #create date and formatting for csv file writing
    ids,url,desc,date,last,multi,resolved   = ([],[],[],[],[],[],[])
    msgid,categ,rj,scores,hits              = ([],[],[],[],[])
    timefrmt,times       = (None,None)
    count,bzcount,total  = (0,0,0)
    button   = '<button type=submit>Take Selected Tickets</button>' \
             '</form>'
    closebtn = '<button type=submit>Resolve Tickets</button>' \
             '</form>'
    if flag == True: # creates the assigned html page with all your open tickets
        hdrs = ["Link","Description","DateOpened","LastModified", "Bulk Resolve"]
        url  = list(itertools.chain.from_iterable(settings.filedata['Link']))
        desc = list(itertools.chain.from_iterable(settings.filedata['Description']))
        date = list(itertools.chain.from_iterable(settings.filedata['DateOpened']))
        last = list(itertools.chain.from_iterable(settings.filedata['LastModified']))
        ids  = list(itertools.chain.from_iterable(settings.filedata['ID']))
        total = len(url)
        for c in url:
            if "bugzilla" not in c:
                count+=1
            else:
                bzcount+=1
        for i in ids:
            chkboxes = '<form action=/bulkresolve method=POST>'\
                '<input type=checkbox name=resolve value='+i+'>' \
                '<label for='+i+'>'+i+'</label><br>'
            resolved.append(chkboxes)
    elif flag == "juno1": # fp/fn for username
        hdrs = ["FP/FN Submissions for User: "+ settings.uname,"Submitted Time"]
        if len(settings.elasticqrys['cids']) >= 1:
            msgid = settings.elasticqrys['cids']
            times = settings.elasticqrys['category']
        else:
            msgid = "None"
            times = "None"
    elif flag == "juno2": # sha256
        hdrs = ["CIDS", "Dates"]
        if len(settings.elasticqrys['cids']) >= 1:
            msgid = settings.elasticqrys['cids']
            date  = settings.elasticqrys['dates']
        else:
            msgid = "None"
            times = "None"
    elif flag == "juno3": # senderip
        hdrs = ["CIDS","DATE"]
        msgid = settings.elasticqrys['cids']
        dates = settings.elasticqrys['cats']
    elif flag == "juno4": #sender email
        hdrs = ["CIDS"]
    elif flag == "juno": # domains
        hdrs  = ["cid", "category"]
        msgid = settings.elasticqrys['cids']
        categ = settings.elasticqrys['cats']
    elif flag == "cmd": #talos guid to cmd converter
        hdrs   = ["Coverted CID","Date"]
        msgid.append(settings.guidconvert['cid'])
        timest = settings.guidconvert['date']
        timefrmt = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timest))
    elif flag =="rj":
        hdrs = ["CID"]
    elif flag == "sbjat":
        hdrs    = ["Tickets", "Date", "Score", "Hits"]
        ids     = settings.sbjatresults['tickets']
        date    = settings.sbjatresults['date']
        scores  = settings.sbjatresults['scores']
        hits    = settings.sbjatresults['hits']
    else: # loads the unassigned page with take ticket button and checkboxes
        hdrs = ["Link", "Description","Created", "Assign"]
        url  = list(itertools.chain.from_iterable(settings.filedata['Link']))
        desc = list(itertools.chain.from_iterable(settings.filedata['Description']))
        date = list(itertools.chain.from_iterable(settings.filedata['DateOpened']))
        ids  = list(itertools.chain.from_iterable(settings.filedata['ID']))
        total = len(url)
        for c in url:
            if "COG" in c:
                count+=1
            else:
                bzcount+=1
        for i in ids:
            chkboxes = '<form action=/takescript method=POST>'\
                '<input type=checkbox name=checks value='+i+'>' \
                '<label for='+i+'>'+i+'</label><br>'
            multi.append(chkboxes)
    #write csv file
    with open(settings.csvfname, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(hdrs)
        if flag == "juno1": # fp/fn submissions
            for row in range(int(len(msgid))):
                writer.writerow([msgid[row],times[row]])
        elif flag == "juno2": # sha 256
            for row in range(int(len(msgid))):
                writer.writerow([msgid[row], date[row]])
        elif flag == "juno3":  # sender ip
            for row in range(int(len(msgid))):
                writer.writerow([msgid[row], dates[row]])
        elif flag == "juno":
            for row in range(int(len(msgid))):
                writer.writerow([msgid[row],categ[row]])
        elif flag ==  True: # assigned tickets
            for row in range(int(len(date))):
                writer.writerow([url[row],desc[row],date[row],last[row],resolved[row]])
            writer.writerow(['','','','', closebtn])
            writer.writerow(["Total Opened",total])
            writer.writerow(["Jira",count])
            writer.writerow(["Bugzilla",bzcount])
        elif flag == "cmd": # cmd guid to cid
            for row in range(int(len(msgid))): # write cid and date
                writer.writerow([msgid[row],timefrmt])
            # writes the reinjection results for the cid
            for row in range(int(len(msgid))):
                #print(int(len(settings.guidconvert['rj'])))
                writer.writerow(["Sherlock Reinjection Results"])
            for i in settings.guidconvert['rj']:
                writer.writerow([i])
            #sbrs data for the sending ip if any
            if len(settings.guidconvert['sbrs']) > 0:
                writer.writerow([settings.guidconvert['sbrs']])
            # tracker decoder scores data
            trackerhdrs = ['Eng', 'Score', 'Verdict', 'Header Present', 'SBRS']
            writer.writerow(trackerhdrs)
            writer.writerows([settings.guidconvert['esascores']])
            writer.writerows([settings.guidconvert['corpscores']])
            writer.writerows([settings.guidconvert['rjscores']])
            writer.writerow('\n')
            settings.guidconvert.clear() # empty dict
        elif flag == "rj":
            for i in settings.guidconvert['rj']:
                writer.writerow([i])
        elif flag == "sbjat":
            if "None" in ids[0] or len(ids) == 0:
                writer.writerow(['None','None','N/A','N/A'])
            else:
                for row in range(int(len(ids))):
                    writer.writerow([ids[row],date[row],scores[row],hits[row]])
        else: # write unassigned csv file
            for row in range(int(len(multi))):
                writer.writerow([url[row],desc[row],date[row],multi[row]])
            writer.writerow(['','','',button])
            writer.writerow(["Total Opened",total])
            writer.writerow(["Jira",count])
            writer.writerow(["Bugzilla",bzcount])
        f.close()

def htmloutput(fname): # wrtite html file from the csv file
    homelink = '<p><a href="/layout">Home | </a><a href="/assigned">Assigned</a > ' \
               '<a href="/unassigned"> | Unassigned</a><a href="/getacetix"> | ACE Tix</></p>\n'
    filein = open(settings.csvfname, "r")
    fileout = open(fname, "w")
    data = filein.readlines()
    print(data)
    if "unassigned" in fname:
        hdr = "Unassigned"
    elif "assigned" in fname:
        hdr = "Assigned"
    elif "elastic" in fname:
        hdr = "Juno Elastic Query API Results"
        homelink = '<p><a href="/layout">Home | </a><a href="/elasticq">Elastic Qrys</a></p>\n'
    elif "guid" in fname:
        hdr  = "GUID -> CID Converter with Reinjection"
    elif "rj" in fname:
        hdr = "Sherlock API Reinjection Results"
    elif "sbjat" in fname:
        hdr = "SBRS Jira Automation Tool - SBJAT"
    else:
        hdr = "Error Page"
    css = "<html>\n" \
          "<head>\n" \
          "<link rel='stylesheet' href = '{{ url_for('static', filename='css/main.css') }}'>\n" \
          "<h1 class='logo'>"+hdr+"</h1>\n" \
          "</head>\n" \
          "<body>"
    table = css
    table += "\n<div class='tblcontainer'>\n" \
            "<table class='tbl'>\n"
    table += "<style>\n" \
            "table, th, td {\n" \
                "border: 1px solid black;\n" \
                "border-collapse: collapse;\n" \
            "}\n" \
            "</style>\n" \
            "<table style='width:100%'>\n"
    table+=homelink
    # Create the table's column headers
    header = data[0].split(",")
    table += "  <tr>\n"
    for column in header:
        table += "    <th>{0}</th>\n".format(column.strip())
    table += "  </tr>\n"
    # Create the table's row data
    for line in data[1:]:
        row = line.split(",")
        table += "  <tr>\n"
        for column in row:
            table += "    <td>{0}</td>\n".format(column.strip())
        table += "  </tr>\n"
    table   += "</table>\n</div>\n"
    footer   = "<div class=footer>\n" \
               "<p>Copyright (c) 2022 wikoeste, Cisco Internal Use Only</p>\n" \
               "</div>\n"
    table += footer
    table += "</body>\n" \
             "</html>"
    fileout.writelines(table)
    fileout.close()
    filein.close()
