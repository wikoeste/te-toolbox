from liono.common import settings
settings.init()
import requests,textwrap
from terminaltables import AsciiTable

def quickssearch(params):
    bzurl   = 'https://bugzilla.vrt.sourcefire.com/rest/bug'
    resp    = requests.get(bzurl, params= params,  verify = False)
    ids,resolution,status,isopen,reporturls,owners,summs,shrtsums = ([],[],[],[],[],[],[],[])
    if resp.status_code == 200:
        jresp = resp.json()
        #print("BZ API Search",json.dumps(jresp, indent=2))
        total = len(jresp['bugs'])
        if total == 0:
            settings.bzsearchresults.update({'noresults': 'none'})
        else:
            for i in jresp['bugs']:
                if i['is_open'] is True:
                    isopen.append('YES')
                    ids.append(str(i['id']))
                    resolution.append(i['resolution'])
                    status.append(i['status'])
                    owners.append(i['assigned_to_detail']['name'])
                    summs.append(i['summary'])
                    reporturls.append('https://bugzilla.vrt.sourcefire.com/show_bug.cgi?id={}'.format(i['id']))
                    #join all lists to strings on new lines
                    resol   = "\n".join(resolution)
                    stats   = "\n".join(status)
                    owner   = "\n".join(owners)
                    opened  = "\n".join(isopen)
                    urls    = "\n".join(reporturls)
                    bugs    = "\n".join(ids)
            #total   = len(ids)
            totalopened = sum(1 for i in isopen if i == "YES")
            totalclosed = sum(1 for i in isopen if i == "NO")
            reviewed    = sum(1 for x in status if x == "REVIEWED")
            for x in summs:
                short = textwrap.shorten(x,width=75,placeholder="[...]")
                shrtsums.append(short)
            smry    = "\n".join(shrtsums)
            #configure BZ Search tables
            data = [["BZ Link","Summary","Status","Opened","Owner"],
                [bugs,smry,stats,opened,owner]]
            bzResults = AsciiTable(data, "Bugzilla Case Search Results")
            print(bzResults.table)
            settings.bzsearchresults.update({'bugs':bugs})
            settings.bzsearchresults.update({'smry':smry})
            settings.bzsearchresults.update({'stats':stats})
            settings.bzsearchresults.update({'opened':isopen})
            settings.bzsearchresults.update({'owner':owner})
    else:
        error       = ("BZ HTTP API ERROR {}".format(resp.status_code))
        tbldata     = [["Bugzilla Tickets", "Error"],["None Found", error]]
        bzResults   = AsciiTable(tbldata, "Bugzilla Ticket Search")
        print(bzResults.table)
        settings.bzsearchresults.update({'err':tbldata})

def bzhtml(hdrs):
    # break off to function
    table = ""
    css = "<html>\n" \
          "<head>\n" \
          " <link rel='stylesheet' href = '{{ url_for('static', filename='css/main.css') }}'>\n" \
          "<title>Ticket Results</title>\n" \
          "<h1 class='logo'> Bugzilla API Quick Search</h1>\n" \
          "</head>\n" \
          "<body>"
    table = css
    table += "<style>\n" \
             "table, th, td {\n" \
             "border: 1px solid black;\n" \
             "border-collapse: collapse;\n" \
             "}\n" \
             "</style>\n" \
             "<table style='width:100%'>\n"
    table += "  <tr>\n"
    for column in hdrs:
        table += "    <th>{0}</th>\n".format(column.strip())
    table += "  </tr>\n"
    for k, v in settings.bzsearchresults.items():
        table += "<td>" + str(v) + "</td>\n"
    table += "</table>\n"
    homelink = '<p><a href="/layout">Home | </a><a href="/assigned">Assigned</a > <a href="/unassigned"> | Unassigned</a ></p>\n'
    footer = "<div class=footer>\n" \
             "<p>Copyright (c) 2022 wikoeste, Cisco Internal Use Only</p>\n" \
             "</div>\n"
    table += homelink
    table += footer
    table += "</body>\n" \
             "</html>"
    # write html file
    with open(settings.bzsearchresultshtml, "w") as f:
        f.write(table)
    f.close()