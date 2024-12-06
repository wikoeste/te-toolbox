from liono.common import settings
from liono.common import getTickets
from liono.common import csvtohtml
from liono.logging import logger
import os.path,threading
#MAIN#
def main(pw):
    logger.log("==TE1 CaseManager UI ==")
    logger.log("User: {}".format(settings.uname))
    threads = []
    flag    = True
    #t1 = threading.Thread(target = getTickets.bugzilla, args=(flag, ))
    t2 = threading.Thread(target = getTickets.jira, args=(settings.talosjira, flag, pw))
    #threads.append(t1)
    threads.append(t2)
    for t in threads:
        t.start()
        try:
            t.join()
        except Exception as e:
            logger.log(e)
    if settings.filedata is not None:
        csvtohtml.writedata(flag)
        csvtohtml.htmloutput(settings.htmlfname)
        fileExists = os.path.exists(settings.htmlfname)
        exists = ("The file, ", settings.htmlfname +",exists: {}".format(fileExists))
        logger.log(exists)
    else:
        logger.log("No file data in filedata variables from settings")
        logger.log("Or some other error in csv creation")
    # Get unassigned tickets
    getTickets.unassigned(pw)
    threads.clear()
######################
# Run Main As Program
if __name__ == "__main__":
    main()