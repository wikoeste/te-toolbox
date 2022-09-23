from flask import Flask, render_template, request, redirect, session, url_for
import re, json
from liono import main as loader
from liono.common import settings
settings.init()
from liono.common import assignTickets
from liono.common import getTickets
from liono.common import q
from liono.common import csvtohtml
from liono.common import guidtocid
from liono.common import sherlock
from liono.common import bzsearch as bz
from liono.common import aceqrys
from liono.common.sbjat import sbjat as sbrs
####
app = Flask(__name__)
app.secret_key = '3R!n7665'
###Global session vars
cecpw = ''

@app.route('/') #index
def home():
    if 'username' in session:
        username = session['username']
        print('Logged in as ' + username)
        return redirect('/layout')
    return redirect('/notloggedin')

# Web templates
@app.route('/layout')
def layout():
    if 'username' in session:
        return render_template('layout.html')
    return redirect('/notloggedin')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/langs')
def langs():
    return render_template('lang.html')

@app.route('/backlogbuddy')
def backlogbuddy():
    return render_template('backlogbuddies.html')

@app.route('/elasticq')
def elasticqueries():
    return render_template(('/elasticqrys.html'))

@app.route('/unassigned')
def unassigned():
    #shutil.copyfile('/Users/wikoeste/unassigned.html', './templates/unassigned.html')
    return render_template('unassigned.html')

@app.route('/assigned')
def assigned():
    return render_template('assigned.html')

@app.route('/acetickets')
def acetickets():
    return render_template('acetickets.html')

#Tools
@app.route('/cmdtool')
def cmdtool():
    return render_template(('/cmdtool.html'))

@app.route('/bzsearch')
def bzsearch():
    return render_template('/bzsearch.html')

@app.route('/reinjection')
def reinjection():
    return render_template('/reinjectionform.html')


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
        cecpw               = password
        if username == settings.uname:
            loader.main() # run que searches
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

#<!--Scripts executed below-->
@app.route('/runscript/') # get the ticket data for user
def runscript():
    if 'username' not in session:
        return render_template('login.html')
    else:
        loader.main()  # run que searches
        return render_template('assigned.html')

@app.route('/takescript', methods = ['POST','GET']) # assign tickets
def takescript(): # assign ticketsmpty
    # print(request.method)
    print(request.values)
    if request.method == 'POST':
        jsondata = request.json
        print(jsondata)
        selected = request.form.getlist('checks')
        print('the list of tix are {}'.format(selected))
        if selected != "":
            for i in selected:
                assignTickets.assignque(i)
        getTickets.unassigned()  # get the new unassigned tickets after taking one from the list
        return redirect('/unassigned') # reload the unassigned paged
    else:
        return render_template('/takeresults.html') # this should be an error page!

@app.route('/bulkresolve', methods = ['POST']) # close cases
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
            loader.main()  # run que searches
            return redirect('/assigned')  # reload the unassigned paged
    else:
        return render_template('/takeresults.html')  # this should be an error page

@app.route('/getacetix')
def getacetix():
    aceqrys.get_ace_dispute()
    return render_template('/acetickets.html')

@app.route('/talosjiratickets') # get tickets from talos jira instance for the user
def talosjiratickets():
    if 'username' not in session:
        return redirect('notloggedin.html')
    else:
        settings.filedata = {"ID":[],"Link":[],"Description":[],"DateOpened":[],"LastModified":[]}
        getTickets.jira(settings.talosjira,True,session['pw'],settings.que)
        if settings.filedata is not None:
            csvtohtml.writedata(True)
            csvtohtml.htmloutput(settings.htmlfname)
            for q in settings.que.queue:
                print(q.table)
            return render_template('assigned.html')
        else:
            return render_template('error.html')

@app.route('/umbrjiratickets/') # get tickets from talos jira instance for the user
def umbrjiratickets():
    if 'username' not in session:
        return redirect('notloggedin.html')
    else:
        settings.filedata = {"ID":[],"Link":[],"Description":[],"DateOpened":[],"LastModified":[]}
        getTickets.jira(settings.umbjira,True,"S0urc3f1r3!",settings.que)
        if settings.filedata is not None:
            csvtohtml.writedata(True)
            csvtohtml.htmloutput(settings.htmlfname)
            for q in settings.que.queue:
                print(q.table)
            return render_template('assigned.html')
        else:
            return render_template('error.html')

@app.route('/getelastic', methods = ['POST']) # juno qrs
def getelastic():
    flag = "juno"
    if request.method   == 'POST':
        # print(request.values)
        # run the associated elastic query
        if request.form.get('username') == settings.uname:
            q.submissions(settings.uname+"@cisco.com")
            flag = "juno1" # username
        elif re.search(r'[A-Fa-f0-9]{64}', request.form.get('sha256')):
            flag = "juno2" # sha256
            q.sha256(request.form.get('sha256'))
        elif re.search('r^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',request.form.get('ip')):
            flag = "juno3" # senderip
            q.senderip(request.form.get('ip'))
        elif re.search(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', request.form.get('sender')):
            flag = "juno4" # senderemail
            q.senderemail(request.form.get('sender'))
        else:
            q.fromdomain(request.form.get('domain'))
        csvtohtml.writedata(flag)
        csvtohtml.htmloutput(settings.elastichtml)
        #shutil.copyfile(settings.homedir+"/elasticresults.html", './templates/elasticresults.html')
        return(render_template('elasticresults.html'))

@app.route('/getcid', methods = ['POST','GET']) # talos guid to cid
def getcid():
    if request.method == 'POST':
        #print(request.values)
        guid = request.form.get('guid')
        guidtocid.getcid(guid)
        flag = "cmd"
        csvtohtml.writedata(flag)
        csvtohtml.htmloutput(settings.cmdresultshtml)
        return (render_template('guidconvertresults.html'))

@app.route('/bzsearchresults', methods = ['POST'])
def bzsearchresults():
    hdrs = ["BZ Link", "Summary", "Status", "Opened", "Owner"]
    if request.method == 'POST':
        query = request.form.get('string')
        params = {'product': ['escalations', 'research'], 'quicksearch': query,
            'creation_time': settings.lastninety,'api_key': settings.bzKey}
        print(request.method, query)
        bz.quickssearch(params)
        bz.bzhtml(hdrs)
        return render_template('bzsearchresults.html')
    else:
        print("Error with getting bz quick search api results")
        return render_template('error')

@app.route('/getrj', methods = ['POST','GET']) # get rj results from cid
def getrj():
    if request.method == 'POST':
        #print(request.values)
        #cid  = request.form.get('cid')
        #print(cid)
        text        = request.form['cid']
        frmtedtext  = text
        frmtedtext  = frmtedtext.replace("\r",'')
        frmtedtext  = frmtedtext.replace(" ", "")
        cidlist     = frmtedtext.split("\n")
        cids        = [i for i in cidlist if i.strip()]
        for cid in cids:
            sherlock.reinjection(cid,settings.uname,settings.sherlockKey,settings.que)
            flag = "rj"
            csvtohtml.writedata(flag)
            csvtohtml.htmloutput(settings.rjresultshtml)
        settings.guidconvert.clear()  # empty dict
        guidconvert = {"cid": [], "date": "", "rj": [], "esascores": [], 'corpscores': [], 'rjscores': [], 'sbrs': []}
        return (render_template('rjresults.html'))

@app.route('/sbjat') # get sbrs results from jira
def sbjat():
    #Run sbjat tool & Convert data to html page
    if 'username' not in session:
        return render_template('notloggedin.html')
    else:
        sbrs.sbrsauto(session['pw'])
        return render_template('sbjat.html')
#############
if __name__ == '__main__':
    app.run(debug=True)
