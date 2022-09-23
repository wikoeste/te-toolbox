from liono.common import settings
from liono.common import getTickets
from liono.common import csvtohtml
from liono.common import bzsearch
from liono.logging import logger
import os.path,threading,sys,pandas
#MAIN#
def main():
    logger.log()
    threads = []
    flag    = True
    print("==TE1 CaseManager UI ==")
    t1 = threading.Thread(target = getTickets.bugzilla, args=(flag,settings.que ))
    t2 = threading.Thread(target = getTickets.jira, args=(settings.tejira,flag,settings.cec,settings.que))
    #t3 = threading.Thread(target=getTickets.jira, args=(settings.talosjira,flag,settings.cec,settings.que))
    #t4 = threading.Thread(target=getTickets.jira, args=(settings.umbjira,flag,settings.umb,settings.que))
    #t5 = threading.Thread(target=getTickets.analystconsole, args=(flag,settings.que, ))
    threads.append(t1)
    threads.append(t2)
    #threads.append(t3)
    #threads.append(t4)
    #threads.append(t5)
    for t in threads:
        t.start()
        try:
            t.join()
        except Exception as e:
            print("Error running thread...{}".format(e))
    if settings.filedata is not None:
        csvtohtml.writedata(flag)
        csvtohtml.htmloutput(settings.htmlfname)
        fileExists = os.path.exists(settings.htmlfname)
        print("The file, ", settings.htmlfname +",exists: {}".format(fileExists))
        #os.remove(settings.csvfname) #remove csv file
        #os.chdir('static')
        #langfile     = pandas.read_csv('langacr.csv')
        #backlogbuddy = pandas.read_csv('backlogbuddy.csv')
        #langfile.to_html('../templates/lang.html')
        #backlogbuddy.to_html('../templates/backlogbuddies.html')
    else:
        print("No file data in filedata variables from settings")
        print("Or some other error in csv creation")
    # Get unassigned tickets
    getTickets.unassigned()
    # Print the table results
    for q in settings.que.queue:
        print(q.table)
    threads.clear()
    
######################
# Run Main As Program
if __name__ == "__main__":
    main()