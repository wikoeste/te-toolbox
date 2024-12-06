# Source: https://confluence.vrt.sourcefire.com/display/TET/
# CMD+-+Cisco+Secure+Email+Cloud+Mailbox
######
from liono.common import settings
from liono.common import sherlock
from liono.common import q
import requests,json,re,getpass,os,queue
requests.packages.urllib3.disable_warnings()
###
def getcid(guid): # get the cid using the guid input
    twelve  = "juno_past_12_months/_search?filter_path"
    hdrs    = {"Content-type":"application/json"}
    qry     = '{"_source": ["date", "add_timestamp"],"size": 100,"query": ' \
        '{"term": {"taln_ingest_result.message_guid": {"value": "'+guid+'"}}}}'
    resp    = requests.get(settings.juno+twelve,headers=hdrs,data=qry,auth=(settings.uname,settings.junoKey),verify=False)
    cid,date = ('0','0')
    if resp.status_code == 200:
        jresp = resp.json()
        #print(json.dumps(jresp, indent=2))
        if jresp["hits"]["total"] > 0:
            #print(str(jresp['hits']['total']))
            cid  = jresp["hits"]["hits"][0]["_id"]
            date = jresp["hits"]["hits"][0]["_source"]["date"]
            settings.guidconvert['cid'] = cid
            settings.guidconvert['date'] = date
            sherlock.reinjection(cid, settings.uname, settings.sherlockKey,settings.que)
        else:
            settings.guidconvert['cid'] = "None"
            settings.guidconvert['date'] = "N/A"
    else:
        err = "HTTP ERROR {}".format(resp.status_code)
        settings.guidconvert['cid'] = err
        settings.guidconvert['date'] = "N/A"
    #print("Guid to cid conversion, " + str(settings.guidconvert))

#taln_ingest_result.message_guid":
# {"value": "9acf4475-dcac-4707-ace5-d5fc1fc168d0"}