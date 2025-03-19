from liono.common import settings
settings.init()
import requests,json,time,re
requests.packages.urllib3.disable_warnings()
from terminaltables import AsciiTable
from datetime import datetime

def submissions(username): # last 24 hours
    eqry      = '{"_source": ["_id","@timestamp","add_timestamp","date"],"size": 200,"query":{"bool": {"must": [{"term":{"reporter.address_raw":"'+username+'"}}]}}}'
    headers   =  {'Content-type': 'application/json'}
    now       = time.time()
    cids,ts   = ([],[])
    try:
        urlRequest = requests.get (settings.juno+"juno_past_1_month/_search?",headers=headers, data=eqry, auth=(settings.uname,settings.junoKey), verify=False, stream=True, timeout=200)
        status = urlRequest.status_code
        if status == 200:
            json_result =urlRequest.json()
            #print(json.dumps(json_result, indent=2))
            total = json_result["hits"]["total"]["value"]
            if int(total) > 0:
                for i in json_result["hits"]["hits"]:
                    timestamp = i['_source']['@timestamp']
                    subtime = timeconverter(timestamp)
                    diff = int(now) - int(subtime)
                    if int(diff) < 86400:
                        cids.append(i['_id'])
                        ts.append(timestamp)
                cidString  = '\n'.join(cids)
                timeString = '\n'.join(ts)
                tbldata = [['FP/FN submissions by: ' + username, 'Date'],
                    [cidString, timeString]]
                submissiontbl = AsciiTable(tbldata)
                #print(submissiontbl.table)
                settings.elasticqrys.update({'cids':cids})
                settings.elasticqrys.update({'category':ts})
                #print(settings.elasticqrys)
            else:
                tbldata         = [['FP/FN submissions by: '+username]]
                submissiontbl   = AsciiTable(tbldata)
                #print(submissiontbl.table)
        else:
            tbldata = [['FP/FN submissions by: '+username],["HTTP Error {}".format(status)]]
            submissiontbl = AsciiTable(tbldata)
            #print(submissiontbl.table)
    except requests.exceptions.Timeout as e:
        print("Timeout exception to Juno server.")

def fromdomain(sender): # last 90 days
    settings.elasticqrys.clear()
    query   = '{"size": 25,"_source": ["message_id", "category"],"query": {"bool": {"must": [{"nested": {"path": "froms","query": {"term": ' \
              '{"froms.address_domain":"'+sender+'"}}}}]}}}'
    headers =  {'Content-type': 'application/json'}
    try:
        response = requests.get(settings.juno90, headers=headers, data=query, auth=(settings.uname,settings.junoKey), verify=False, timeout=120, stream = True)
        status = response.status_code
        if status == 200:
            json_result = response.json()
            print(json.dumps(json_result, indent=2))
            total                   = json_result['hits']['total']["value"]
            cids,cats               = ([],[])
            if total > 0:
                for i in json_result['hits']['hits']:
                    #cids.append(i['_id'])
                    settings.elasticqrys['cids'].append(i['_id'])
                    settings.elasticqrys['cats'].append(i['_source']['category'])
            else:
                tbldata = [["CIDS from: "+ sender,cids,0,"N/A"]]
                fromDomainSampleTbl = AsciiTable(tbldata)
                #print(fromDomainSampleTbl.table)
                settings.elasticqrys['cids'].append("CIDS from: "+ sender)
                settings.elasticqrys['cats'].append("N/A")
        else:
            settings.elasticqrys['cids'].append("CIDS from: " + sender)
            settings.elasticqrys['cats'].append(status)
    except requests.ConnectionError as e:
        settings.elasticqrys['cids'].append("Juno Server Timouet")
        settings.elasticqrys['cats'].append("Try again later")

def sha256(sample): # 12 month search
    qry     = '{"size": 10,"_source": ["message_id","add_timestamp", "@timestamp"],"query": {"bool": {"must": [{"nested": {"path": "attachments","query":' \
              ' {"term": {"attachments.sha256":"'+sample+'"}}}}, {"range": {"add_timestamp": {"gte": "now-180d","lt": "now"}}}]}}}'
    headers =  {'Content-type': 'application/json'}
    try:
        response = requests.get(settings.juno+"juno_past_12_months/_search?", headers=headers,data=qry,auth=(settings.uname,settings.junoKey),
            verify=False,timeout=120, stream=True)
        if response.status_code == 200:
            jresult = response.json()
            json_result = response.json()
            print(json.dumps(json_result, indent=2))
            settings.elasticqrys.update({'cids': []})
            settings.elasticqrys.update({'dates': []})
            '''
            {
                "took": 6757,
                "timed_out": false,
                "_shards": {
                    "total": 80,
                    "successful": 80,
                    "skipped": 0,
                    "failed": 0
                },
                "hits": {
                    "total": 1,
                    "max_score": 11.348387,
                    "hits": [
                        {
                            "_index": "juno_v5_2022_01",
                            "_type": "doc",
                            "_id": "cidG50061eq1V4RX12qA53e3tCe4aSz9nOo7",
                            "_score": 11.348387,
                            "_source": {
                                "add_timestamp": 1642084119,
                                "message_id": "cidG50061eq1V4RX12qA53e3tCe4aSz9nOo7"
                            }
                        }
                    ]
                }
            }
            '''
            if json_result["hits"]["total"]["value"] > 0:
                # get message & time stampe
                for i in json_result["hits"]["hits"]:
                    settings.elasticqrys["cids"].append(i["_id"])
                    #these times stamps need converted to readable human
                    settings.elasticqrys["dates"].append(i["_source"]["@timestamp"])
            else:
                settings.elasticqrys["cids"].append("None")
                settings.elasticqrys["dates"].append("--")
        else:
            err = "HTTP ERROR {}".format(response.status_code)
            attachmentTable = AsciiTable([['Juno API'],[err]])
            #print(attachmentTable.table)
    except requests.ConnectionError as e:
        attachmentTable = AsciiTable([['Juno API'],["Server Timeout"]])
        #print(attachmentTable.table)

def senderemail(fromaddr): # 12 month search
    qry     = '{"size": 100,"_source": ["message_id","ipas.ingest.spam_score","category","add_timestamp","vof_score.ingest"],"query": {"bool": {"must": [{"nested": {"path": "froms","query": {"term": {"froms.address_raw": "'+fromaddr+'"}}}}]}}}'
    headers =  {'Content-type': 'application/json'}
    cids,scores,cats,timestamp = ([],[],[],[])
    total = 0
    try:
        response = requests.get(settings.juno+"juno_past_12_months/_search?", headers=headers,data=qry, auth=(settings.uname,settings.junoKey),
            verify=False, timeout=120, stream = True)
        if response.status_code == 200:
            jresult = response.json()
            #print(json.dumps(jresult, indent=2))
            total = jresult['hits']['total']['value']
            if total > 0:
                #print(json.dumps(jresult, indent=2))
                for i in jresult["hits"]["hits"]:
                    cids.append(i["_id"])
                    scores.append(str(round(i["_source"]["ipas.ingest.spam_score"],2)))
                    cats.append(i["_source"]["category"])
                    sampletime = i["_source"]["add_timestamp"]
                    tstamp = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(sampletime))
                    timestamp.append(tstamp)
                cid     = "\n".join(cids[:10])
                scr     = "\n".join(scores[:10])
                categ   = "\n".join (cats[:10])
                times   = "\n".join(timestamp[:10])
                tbldata = [
                    ["Total Submissions","CIDS (10)","Category","Ingest Score","Timestamp"],
                    [str(total),cid,categ,scr,times],
                ]
                fromTable = AsciiTable(tbldata,'Juno Results: Sender Address: ' + fromaddr)
                print(fromTable.table)
            else:
                fromTable = AsciiTable([['Juno Results: Sender Address ' +fromaddr],["No Results"]])
                print(fromTable.table)
        else:
            err = "Http ERROR {}".format(response.status_code)
            fromTable = AsciiTable([['Juno API Timeout'],[err]])
            print(fromTable.table)
    except requests.ConnectionError as e:
        fromTable = AsciiTable([['Juno API Timeout']])
        print(fromTable.table)

def senderip(ip): # 12 months max 50 results
    qry     = '{"size":50,"_source":["message_id","add_timestamp"],"query":{"term":{"sender_ip":"'+ip+'"}}}'
    headers =  {'Content-type': 'application/json'}
    cids,cats,scores,timestamps = ([],[],[],[])
    total = 0
    try:
        response = requests.get(settings.juno+"juno_past_12_months/_search?", headers=headers,data=qry, auth=(settings.uname,settings.junoKey),verify=False,timeout=120,stream=True)
        if response.status_code == 200:
            jresult = response.json()
            print(json.dumps(jresult, indent=2))
            total = jresult['hits']['total']['value']
            if total > 0:
                print(json.dumps(jresult, indent=2))
                for i in jresult["hits"]["hits"]:
                    settings.elasticqrys["cids"].append(i["_id"])
                    ts = i["_source"]["add_timestamp"]
                    tsreadable = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(ts))
                    tsfrmt = re.sub(',', ' ', tsreadable)
                    settings.elasticqrys["cats"].append(tsfrmt)
            else:
                settings.elasticqrys["cids"].append("None")
                settings.elasticqrys["cats"].append("--")
        else:
            print("Error HTTP {}".format(response.status_code))
    except requests.ConnectionError as e:
        print("ERROR Reaching Juno server!")

def subject(subjstr):
    qry = '{"size":10,"_source":["message_id","@timestamp","ipas.ingest.spam_score","category"],' \
          '"query":{"term":{"subject.raw":"' + subjstr  + '"}}}'
    headers = {'Content-type': 'application/json'}
    total = 0
    try:
        response = requests.get(settings.juno+"juno_past_12_months/_search?", headers=headers,data=qry, \
            auth=(settings.uname,settings.junoKey),verify=False, timeout=120, stream=True)
        if response.status_code == 200:
            jresult = response.json()
            print(json.dumps(jresult, indent=2))
            total = jresult['hits']['total']['value']
            if total > 0:
                # print(json.dumps(jresult, indent=2))
                for i in jresult["hits"]["hits"]:
                    settings.elasticqrys["cids"].append(i["_id"])
                    settings.elasticqrys.update({"scores":str(round(i["_source"]["ipas.ingest.spam_score"], 2))})
                    settings.elasticqrys["cats"].append(i["_source"]["category"])
                    sampletime = i["_source"]["@timestamp"]
                    settings.elasticqrys.update({"timestamps":sampletime})
            else:
                settings.elasticqrys["cids"].append("None")
                settings.elasticqrys["cats"].append("--")
        else:
            print("Error HTTP {}".format(response.status_code))
    except requests.ConnectionError as e:
        print("ERROR Reaching Juno server!")

def etdverdicts(cids):
    etdverd,guid,amp,bd,cape,cua,rap,ret,tg,turs,tuvs,vade,sdrverd = ("--",) * 13
    data         = ""
    results      = [{}]
    hdrs         = {"Content-type":"application/json"}
    print(len(cids))
    for c in cids:
        qry     = '{"_source":["_id","talos_msg_guid","@timestamp","etd.etd_verdict","etd.etd_verdict_ts","etd.dispute_customer_guid","etd.verdict_keywords.amp","etd.verdict_keywords.bd","etd.verdict_keywords.cape",' \
                  '"etd.verdict_keywords.cua","etd.verdict_keywords.raptor","etd.verdict_keywords.ret","etd.verdict_keywords.tg",' \
                  '"etd.verdict_keywords.turs","etd.verdict_keywords.tuvs","etd.verdict_keywords.vade","tos.address_domain","subject",' \
                  '"sdr.verdict_name"],"query":{"term": {"_id": "'+str(c)+'"}}}'
        try:
            response = requests.get(settings.juno + "juno_past_12_months/_search?",headers=hdrs,data=qry,
                auth=(settings.uname,settings.junoKey),verify=False,timeout=120,stream=True)
            if response.status_code == 200:
                jresult = response.json()
                #print(json.dumps(jresult, indent=2))
                total = jresult['hits']['total']['value']
                if total > 0:
                    #print(json.dumps(jresult, indent=2))
                    for i in jresult['hits']['hits']:
                        try:
                            guid = i["_source"]["talos_msg_guid"]
                        except KeyError:
                            guid = "Unknown"
                        try:
                            amp = i["_source"]["etd"]["verdict_keywords"]["amp"]
                        except KeyError:
                            amp = "None"
                        try:
                            bd = i["_source"]["etd"]["verdict_keywords"]["bd"]
                        except KeyError:
                            bd = "None"
                        try:
                            cape = i["_source"]["etd"]["verdict_keywords"]["cape"]
                        except KeyError:
                            cape = "None"
                        try:
                            cua = i["_source"]["etd"]["verdict_keywords"]["cua"]
                        except KeyError:
                            cua = "None"
                        try:
                            rap = i["_source"]["etd"]["verdict_keywords"]["raptor"]
                        except KeyError:
                            rap = "None"
                        try:
                            ret = i["_source"]["etd"]["verdict_keywords"]["ret"]
                        except KeyError:
                            ret = "None"
                        try:
                            tg = i["_source"]["etd"]["verdict_keywords"]["tg"]
                        except KeyError:
                            tg = "None"
                        try:
                            turs = i["_source"]["etd"]["verdict_keywords"]["turs"]
                        except KeyError:
                            turs = "None"
                        try:
                            tuvs = i["_source"]["etd"]["verdict_keywords"]["tuvs"]
                        except KeyError:
                            tuvs = "None"
                        try:
                            vade = i["_source"]["etd"]["verdict_keywords"]["vade"]
                        except KeyError:
                            vade = "None"
                        try:
                            etdverd = i["_source"]["etd"]["etd_verdict"]
                        except KeyError:
                            etdverd = "None"
                        try:
                            sdrverd = i["_source"]["sdr"][0]["verdict_name"]
                        except KeyError:
                            sdrverd = "None"
                        results.append({"cid": i["_id"],"guid":guid,"ts": i["_source"]["@timestamp"],
                                    "verd": etdverd,"amp":amp,"bd":bd,"cape":cape,"cua":cua,"rap":rap,"ret":ret,"tg":tg,
                                    "turs":turs,"tuvs":tuvs,"vade":vade,"sdr":sdrverd})
                else:
                    results.append({"cid":c,"guid":"--","ts":"--","verd":"--","amp":amp,"bd":bd,"cape":"--","cua":"--","rap":"--","ret":"--","tg":"--",
                                    "turs":"--","tuvs":"--","vade":"--","sdr":"--"})
            else:
                results.append({"cid":c,"guid":"--","ts":"--","verd":"--","amp":amp,"bd":bd,"cape":"--","cua":"--","rap":"--","ret":"--","tg":"--",
                                    "turs":"--","tuvs":"--","vade":"--","sdr":"--"})
                print("JSON ERROR:{} ".format(response.status_code)+c)
        except requests.exceptions.Timeout:
            print("Timeout exception to Juno server.")
    #Results of ETD hdrs
    if len(results) > 1:
        del results[0]
        print("Results total = " + str(len(results)))
        for i in results:
            data = ("===ETD Results==="+
            "\nSample: "+ i["cid"]+
            "\nGUID: "+ i["guid"]+
            "\nVerdict: "+ i["verd"]+
            "\nDate: "+ i["ts"]+
            "\n===Engines==="+
            "\n Amp:"+ i["amp"]+"\n"+
            "BD:\t"+i["bd"]+"\n"+
            "Cape:\t"+i["cape"]+"\n"+
            "CUA:\t"+i["cua"]+"\n"+
            "MA:\t"+i["tg"]+"\n"+
            "TURS:\t"+i["turs"]+"\n"+
            "TUVS:\t"+i["tuvs"]+"\n"+
            "Vade:\t"+i["vade"]+"\n"+
            "SDR:\t"+i["sdr"]+"\n")
            #print(data)
            # write the results to global var
            settings.etdresults.append(data)
    else:
        err = "No results for sample: "+str(i)
        # write the results to global var
        settings.etdresults.append(err)

def timeconverter(timestamp):
    p = '%Y-%m-%dT%H:%M:%S.%fZ'
    #mytime = "2009-03-08T00:27:31.807Z"
    epoch = datetime(1970, 1, 1)
    ts = ((datetime.strptime(timestamp, p) - epoch).total_seconds())
    return ts

