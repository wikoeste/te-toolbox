from liono.common import settings
from liono.common import getTickets
from liono.common import csvtohtml
from liono.logging import logger
import os.path,threading
#MAIN#
def main(pw):
    logger.log()
    threads = []
    flag    = True
    print("==TE1 CaseManager UI ==")
    t1 = threading.Thread(target = getTickets.bugzilla, args=(flag, ))
    t2 = threading.Thread(target = getTickets.jira, args=(settings.talosjira, flag, pw))
    threads.append(t1)
    threads.append(t2)
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
    else:
        print("No file data in filedata variables from settings")
        print("Or some other error in csv creation")
    # Get unassigned tickets
    getTickets.unassigned(pw)
    threads.clear()
######################
# Run Main As Program
if __name__ == "__main__":
    main()