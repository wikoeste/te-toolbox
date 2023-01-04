# Senderbase Jira Automation Tool
# Tool to read, analyze, respnde, and resolve jira sbrs case types
# Author: wikoeste
from liono.common import settings, csvtohtml
settings.init()
from liono.common.sbjat import getsbrs
from liono.common.sbjat import postjira
from jira import JIRA
import re

def sbrsauto(cecpw):
    print("===Senderbase Jira Automation Tool (sbjat)===")
    #Collect all SBRS tickets in the last 4 weeks
    options = {"server": "https://jira.talos.cisco.com"}
    jira    = JIRA(basic_auth=(settings.uname, cecpw), options=options)
    #qry    = 'project = COG AND cf[12380] in cascadeOption(14037) AND created >= -24d AND assignee in (EMPTY) ORDER BY key ASC'
    qry    = 'project = COG AND issuetype=SBRS AND created >= -24d AND assignee in (EMPTY) ORDER BY key ASC'

    #qry     = 'project = COG AND resolution is Empty and cf[12380] in cascadeOption(14037) AND created >= -24d AND assignee in (EMPTY) ORDER BY key ASC'
    sbrs    = jira.search_issues(qry, maxResults=100) # get max 100 results
    clist,cmtips   = ([],[])
    cases   = str(sbrs)
    cog     = re.compile("COG-.{5}")
    for match in re.findall(cog, cases): # extract the cog ticket id cog-12345
        # print(match)
        clist.append(match)
    totalsbrstickets = len(clist)
    print('Total sbrs cases in last 24 days is {}'.format(totalsbrstickets))
    print(clist)
    print("=====")
    if len(clist) == 0:
        print("No valid Tickets")
        settings.sbjatresults['tickets'].append("None")
        csvtohtml.writedata("sbjat")
        csvtohtml.htmloutput(settings.sbjathtml)
    else:
        for i in clist:
            # take ownership, parse for data, analyze data, return and post analysis results in private comment, post public boiler plate
            postjira.assign(i, cecpw)
            issue = jira.issue(i)
            issue = jira.issue(i)
            getsbrs.ticketdata(i, cecpw)  # get the ticket data for each cog case located
        csvtohtml.writedata("sbjat")
        csvtohtml.htmloutput(settings.sbjathtml)