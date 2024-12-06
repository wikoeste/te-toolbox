from flask import Flask,render_template,request,redirect,session,url_for,send_from_directory,flash
from werkzeug.utils import secure_filename
import re,json,ipaddress,os
from liono import main as loader
from liono.common import settings
settings.init()
from liono.common import assignTickets,getTickets,q,csvtohtml
from liono.common import sherlock
from liono.common import aceqrys,jsearch,inteldb
from liono.common import ruledownload,snortreplay
from liono.common import rulesearch as rs
import pandas as pd
####
app = Flask(__name__)
app.secret_key = '3R!n7665'
# configure project folders for upload and downloads
RULES_FOLDER       = settings.rulesDir
UPLOAD_FOLDER      = settings.pcapDir
ALLOWED_EXTENSIONS = {'pcap'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RULES_FOLDER']  = RULES_FOLDER
#################################################

# Web templates
@app.route('/') # index
def home():
    if 'username' in session:
        username = session['username']
        print('Logged in as ' + username)
        return redirect('/layout')
    return redirect('/notloggedin')

@app.route('/layout')
def layout():
    if 'username' in session:
        return render_template('layout.html')
    return redirect('/notloggedin')

@app.route('/langs')
def langs():
    return render_template('lang.html')

@app.route('/backlogbuddy')
def backlogbuddy():
    csvtohtml.htmloutput(settings.backlogbuddy)
    return render_template('backlogbuddy.html')

@app.route('/elasticq')
def elasticqueries():
    return render_template('./forms/elasticqrys.html')

@app.route('/unassigned')
def unassigned():
    return render_template('unassigned.html')

@app.route('/assigned')
def assigned():
    return render_template('assigned.html')

@app.route('/acetickets')
def acetickets():
    return render_template('acetickets.html')

@app.route('/jirasearch')
def jirasearch():
    return render_template('./forms/jirasearch.html')

@app.route('/reinjection')
def reinjection():
    return render_template('./forms/reinjectionform.html')

@app.route('/proxysearchform')
def intelproxysearchform():
    return render_template('./forms/intelproxyscript.html')
# END WEB TEMPLATES

##############################
###SNORT3 REPLAY WEB TEMPLATES
@app.route('/pigreplay')                        # run snort 3 replay ui tool
def pigreplay():
    return render_template('./replay/pigreplay.html')

@app.route('/uploadpcap')                        #
def uploadpcap():
    return render_template('./replay/upload.html')

@app.route('/downloadpcap')                        #
def dlpcap():
    return render_template('./replay/download.html')

@app.route('/deletepcap')                        #
def delpcap():
    return render_template('./replay/delete.html')

@app.route('/rulesearch')                        #
def rulesearch():
    return render_template('./replay/rulesearch.html')

@app.route('/ruledl')                        #
def ruledl():
    return render_template('./replay/vrtauth.html')
#END SNORT WEB TEMPLATES
########################

#<!--Login & Logout Page for scripts-->
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')     
        #umbrella = request.form.get('umbrella')
        settings.cec = password
        #settings.umbrella = umbrella
        session['username'] = username
        session['pw']       = password
        settings.cec        = password
        if username == settings.uname:
            loader.main(session['pw']) # run que searches
            return redirect('/assigned')
        else:
            return "<h1>Wrong username or password</h1>\n" \
            "<p><a href=login>Click here to log in.</a></p>\n"
    else:
        return render_template("login.html")

@app.route('/notloggedin')
def notloggedin():
    return render_template('notloggedin.html')

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('login'))
# END login log out scripts
############################
############################
# Ticket Queue actions
# Get tix from jira and bz
# Assign tix
# Resolve tix
##############
# generate html page for assigned,unassigned,ace tix
@app.route('/runscript/')                            # get the ticket data for user
def runscript():
    if 'username' not in session:
        return render_template('login.html')
    else:
        loader.main(session['pw'])  # run que searches
        return render_template('assigned.html')

@app.route('/takescript', methods = ['POST','GET']) # assign tickets base on check box selection
def takescript(): # assign tickets
    #print(request.values)
    if request.method == 'POST':
        jsondata = request.json
        #print(jsondata)
        selected = request.form.getlist('checks')
        print('the list of tix are {}'.format(selected))
        if selected != "":
            for i in selected:
                assignTickets.assignque(i)
        getTickets.unassigned(session['pw'])  # get the new unassigned tickets after taking one from the list
        return redirect('/unassigned') # reload the unassigned paged
    else: # fail to assign generate error
        return render_template('/assignerror.html') 

@app.route('/bulkresolve', methods = ['POST'])      #  bulk close cases
def bulkresolve():
    selected = ""  # empty
    print(request.method)
    print(request.values)
    if request.method == 'POST':
        jsondata = request.json
        selected = request.form.getlist('resolve')
        #print('the list of tix are {}'.format(selected))
        if selected != "":
            for i in selected:
                assignTickets.resolveclose(i)
            loader.main(session['pw'])  # run que searches
            return redirect('/assigned')  # reload the unassigned paged
    else:
        return render_template('/assignerror.html')  # this should be an error page

#ACE q searches
@app.route('/getacetix')                            # get ace tickets from test db and return results
def getacetix():
    aceqrys.get_ace_dispute()
    return render_template('/acetickets.html')

#######################
#Jira ticket q searches
@app.route('/assignedtickets')                      # get tickets from talos jira instance for the user
def assignedtickets():
    if 'username' not in session:
        return redirect('notloggedin.html')
    else:
        loader.main(session['pw'])              # run que searches
        return render_template('assigned.html')

@app.route('/unassignedtickets')                    # get all unassigned tickets from jira cog and bz tickets
def unassignedtickets():
    if 'username' not in session:
        return redirect('notloggedin.html')
    else:
        getTickets.unassigned(session['pw'])
        return redirect('/unassigned')

@app.route('/talosjiratickets')                     # get tickets from talos jira instance for the user
def talosjiratickets():
    if 'username' not in session:
        return redirect('notloggedin.html')
    else:
        settings.filedata = {"ID":[],"Link":[],"Description":[],"DateOpened":[],"LastModified":[]}
        getTickets.jira("all",True,session['pw'])
        if settings.filedata is not None:
            csvtohtml.writedata(True)
            csvtohtml.htmloutput(settings.htmlfname)
            return render_template('assigned.html')
        else:
            return render_template('./err/error.html', err="No tickets found")
        
@app.route('/talosjiraops')
def talosjiraops():
    if 'username' not in session:
        return redirect('notloggedin.html')
    else:
        settings.filedata = {"ID":[],"Link":[],"Description":[],"DateOpened":[],"LastModified":[]}
        getTickets.jira("ops",True,session['pw'])
        if settings.filedata is not None:
            csvtohtml.writedata(True)
            csvtohtml.htmloutput(settings.htmlfname)
            return render_template('assigned.html')
        else:
            return render_template('./err/error.html',err="No Talos OPS tickets found")
        
@app.route('/talosjiraeers')
def talosjiraeers():
    if 'username' not in session:
        return redirect('notloggedin.html')
    else:
        settings.filedata = {"ID":[],"Link":[],"Description":[],"DateOpened":[],"LastModified":[]}
        getTickets.jira("eers",True,session['pw'])
        if settings.filedata is not None:
            csvtohtml.writedata(True)
            csvtohtml.htmloutput(settings.htmlfname)
            return render_template('assigned.html')
        else:
            return render_template('./err/error.html', err="No EERS escalations found.")

@app.route('/talosjirathr')
def talosjirathr():
    if 'username' not in session:
        return redirect('notloggedin.html')
    else:
        settings.filedata = {"ID":[],"Link":[],"Description":[],"DateOpened":[],"LastModified":[]}
        getTickets.jira("thr",True,session['pw'])
        if settings.filedata is not None:
            csvtohtml.writedata(True)
            csvtohtml.htmloutput(settings.htmlfname)
            return render_template('assigned.html')
        else:
            return render_template('./err/error.html')
#END JIRA  Queues

# POST methods
# Search tools and web scripts
@app.route('/getelastic', methods = ['POST']) # juno qrs
def getelastic():
    flag = "juno"
    if request.method   == 'POST':
        print(request.values)
        # run the associated elastic query
        if request.form.get('username') == settings.uname:
            q.submissions(settings.uname+"@cisco.com")
            flag = "juno1" # username
        elif re.search(r'[A-Fa-f0-9]{64}', request.form.get('sha256')):
            flag = "juno2" # sha256
            q.sha256(request.form.get('sha256'))
        elif re.search(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', request.form.get('sender')):
            flag = "juno4" # senderemail
            q.senderemail(request.form.get('sender'))
        elif request.form.get('subj') is not None:
            flag = "juno5"
            q.subject(request.form.get('subj'))
        elif ipaddress.ip_address(request.form.get('ip')):
            flag = "juno3" # senderip
            q.senderip(request.form.get('ip'))
        else:
            q.fromdomain(request.form.get('domain'))
        csvtohtml.writedata(flag)
        if flag == "cmd":
            csvtohtml.writedata(flag)
            csvtohtml.htmloutput(settings.cmdresultshtml)
            return (render_template('guidconvertresults.html'))
        else:
            csvtohtml.htmloutput(settings.elastichtml)
            return(render_template('./results/elasticresults.html'))


#Search umbrella proxy lists for a matching entry
@app.route('/inteldbproxyscript', methods=['POST','GET'])
def inteldbproxyscript():
    print(request.method)
    if request.method   == 'POST':
        print(request.values)
        res = request.values
        if request.form.get('sample') is not None:
            sample = request.form.get('sample')
            inteldb.lookup(sample)
            return render_template('./results/intelproxy-results.html', res=settings.inteldbmatches['url'],feed=settings.inteldbmatches['feed'])
        else:
            err = "Error getting Umbrella Intel Proxy results!"
            return render_template('./err/error.html',err=err)
    settings.inteldbmatches.clear()
    settings.inteldbmatches = {'url':[],'feed':[]}

@app.route('/getrj', methods = ['POST','GET']) # get rj results from cid
def getrj():
    if request.method == 'POST':
        #print(request.values)
        cids  = request.form.getlist('cid')
        cids  = [x.replace("\"","'") for x in cids]
        cids = [x.replace('\r\n', '","') for x in cids]
        sherlock.reinjection(cids,settings.uname,settings.sherlockKey)
        flag = "rj"
        csvtohtml.writedata(flag)
        csvtohtml.htmloutput(settings.rjresultshtml)
        settings.guidconvert.clear()  # empty dict
        settings.guidconvert = {"cid": [], "date": "", "rj": [], "esascores": [], 'corpscores': [], 'rjscores': [], 'sbrs': []}
        return (render_template('./results/rjresults.html'))

###############
# Reporting
@app.route('/getjira', methods = ['POST','GET']) # jira qrys
def getjira():
    results = None
    if request.method   == 'POST':
        print(request.values)
        #res = request.values
        if request.form.get('cve') is not None:
            cve = request.form.get('cve')
            results = jsearch.search("ALL",cve)
        elif re.search(r'[A-Fa-f0-9]{64}', request.form.get('sha256')) is True:
            s256 = request.form.get('sha256')
            results = jsearch.search("ALL",s256)
        elif request.form.get('thr') is not None:
            qry = request.form.get('thr')
            results = jsearch.search("THR",qry)
        elif request.form.get('eers') is not None:
            qry = request.form.get('eers')
            results = jsearch.search("EERS",qry)
        elif request.form.get('resbz') is not None:
            qry = request.form.get('resbz')
            results = jsearch.search("RESBZ",qry)
        return render_template('./results/jirasearchresults.html',res=results)
    else:
        err = ("Error with getting jira search web api results")
        print(err)
        return render_template('./err/error.html',err=err)

#################
#SNORT 3 Replay
# File upload
def allowed_file(filename):                                     # only allow pcap exstention upload
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Sucess function for file upload
@app.route('/success', methods=['POST'])                        # return if file upload is successful
def uploadfile():
    if request.method == 'POST':
        if 'file' not in request.files:                         # check if the post request has the file part
            flash('No file part')
            return redirect('upload')
        file = request.files['file']
        if file.filename == '':                                 # If no file, browser submits an empty file without a filename.
            flash('No selected file')
            return redirect('upload')
        if file and allowed_file(file.filename):
            f     = request.files['file']
            fname = secure_filename(f.filename)
            f.save(app.config['UPLOAD_FOLDER']+fname)
            return render_template("ack.html", name=f.filename)
    else:                                                       # Return Error
        err = "Not a post request for file upload!"
        return render_template("err.html", err=err)

# List the pcaps for download
@app.route('/filedownloads', methods=['GET'])               # list of upload files to save
def list_files():
    upf = []
    for filename in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(path):
            upf.append(filename)
    return render_template('/replay/download.html', files=upf)

# Download the pcap and save the file
@app.route('/download/<path:filename>',methods=['GET'])     # save the file
def download(filename):
    path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(path,filename)

# Select the File/pcap to  Delete
@app.route('/filedeletion', methods=['GET'])                # List the pcaps you can delete
def delfiles():
    upf = []
    for filename in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(path):
            upf.append(filename)
    return render_template('./replay/delete.html',files=upf)

# Delete the selected file
@app.route('/delete/<path:filename>',methods=['GET','POST']) # Execture the deletion of a file
def delete(filename):
    path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
    if os.path.exists(path):
        os.remove(os.path.join(path, filename))
        return render_template('./replay/deleteack.html', name=filename)
    else:
        err = "File does not exist!"
        return render_template('./err/err.html', err=err)
################################################

# Log in with VRT creds to Download  latest snort rules
@app.route('/vrtauth', methods=['POST'])                #gets vrt creds from authform to download snort rules
def auth():
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        session['username'] = username
        session['pw']       = password
        settings.vrt        = password
        if username == settings.uname:
            res = ruledownload.checkrules()
            #ruledownload.gets3rules()
            if res == True:
                return render_template('./replay/ruledownload.html', name="Rule Download successful")
            elif res == False:
                return render_template("./replay/ruledownload.html", name="No rule download needed as last download was 24 hours ago.")
            else:
                return redirect('/')
        else:
            #return "<h1>Wrong username or password</h1>\n" \
            #"<p><a href=/pigreplay.html>Click here to return home.</a></p>\n"
            err = "Wrong username or password!"
            print(err)
            return render_template('/err/err.html', err=err)
    else:
        err = "Error not a POST requst method!"
        print(request.method)
        return render_template('/err/err.html',err=err)
#################################################

#############
# User option to Search Rules for signatures
@app.route('/rulesearchresults', methods=['POST'])        # rule search results
def rulesearchresults():
    if request.method == 'POST':
        if request.form.get('sid') is not None:
            rule = request.form.get('sid')
            rs.snortsig(rule)
            return render_template('/replay/searchresults.html', name=settings.unedited)
        else:
            err = "not a valid snort sig id"
            return render_template('/err/err.html', err=err)
    else:
        err = "Error not a POST requst method!"
        print(request.method)
        return render_template('/err/err.html',err=err)
#################################################

# Select and upload the pcap for Snort Replay & return the results
@app.route('/replay')                                   #replay form
def replay():
    upf = []
    for filename in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(path):
            upf.append(filename)
    return render_template('/replay/replay.html',files=upf)

# Execute pcap replay
@app.route('/testpcap',methods=['POST'])                # execute replay form inputs
def testpcap():
    sid,raw,pcap = (None,None,None)
    if request.method == 'POST':
        #print(request.values)
        #print(request.form['pcaps'])
        sid      = request.form.get("sid")
        raw      = request.form.get("rawrule")
        pcap     = request.form['pcaps']
        if raw is not None and raw != "":
            rs.snortsig(raw)
        if sid is not None and sid != "":
            rs.snortsig(sid)
        # Get network info from the pcap
        pcapdata = snortreplay.replay(pcap)
        # Replay pcap through snort with the user input signature
        results  = snortreplay.s3(pcap)
        if results is not None:
            return render_template('/replay/replayResults.html', results=results, rule=settings.unedited, snortversion=settings.snortversion, pcapdata=pcapdata)
        else:
            err = "No Alerts or other Results"
            return render_template('/err/err.html', err=err)
        sid,raw,pcap = (None, None, None)
    else:
        err ="Not a Post request!"
        return render_template('/err/err.html', err=err)
        sid,raw,pcap = (None, None, None)

###################
###END FUNCTIONS###


###MAIN APPLICATION###
#############
if __name__ == '__main__':
    app.run(debug=True)