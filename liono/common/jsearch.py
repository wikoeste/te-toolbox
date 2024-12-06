from liono.common import settings
from jira import JIRA
import requests,os

# search the various jira q's for string from user for any related tickets
# return a max 10 results per q
#using jkey, readonly
def search(queue,qry):
    results     = None
    res         = []
    options     = {"server": "https://jira.talos.cisco.com"}
    jira        = JIRA(basic_auth=(settings.uname, settings.jkey), options=options)
    jqry        = 'project='+queue+' AND text ~ "'+str(qry)+'" order by key desc'
    # Print the results by queue
    if queue == "COG":
        jqry = 'project=GOG AND text ~ "' + str(qry) + '" order by key desc'
        results = jira.search_issues(str(jqry), maxResults=10)
        print("=== COG Search Results===")
        for r in results:
            print('{}'.format(r.key))
            res.append(r.key)
        return res
    elif queue  == "EERS":
        jqry = 'project=EERS AND text ~ "' + str(qry) + '" order by key desc'
        results = jira.search_issues(str(jqry), maxResults=10)
        print("===EERS Search Results===")
        for r in results:
            print('{}'.format(r.key))
            res.append(r.key)
        return res
    elif queue  == "RESBZ":
        jqry = 'project=RESBZ AND text ~ "' + str(qry) + '" order by key desc'
        results = jira.search_issues(str(jqry), maxResults=10)
        print("===RESBZ Search Results===")
        for r in results:
            print('{}'.format(r.key))
            res.append(r.key)
        return res
    elif queue  == "THR":
        jqry = 'project=THR AND text ~ "' + str(qry) + '" order by key desc'
        results = jira.search_issues(str(jqry), maxResults=10)
        print("===THR Search Results===")
        for r in results:
            print('{}'.format(r.key))
            res.append(r.key)
        return res
    elif queue == "ALL":
        jqry    = 'project in (COG,EERS,THR,RESBZ) AND text ~ "'+str(qry)+'" order by key desc'
        results = jira.search_issues(str(jqry), maxResults=10)
        print("===All Jira Q's Search Results===")
        for r in results:
            print('{}'.format(r.key))
            res.append(r.key)
        return res
    # ERROR
    else:
        err = "Error, there is no ticket queue {}".format(queue)
        print(err)
        return err