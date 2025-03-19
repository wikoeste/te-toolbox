from liono.common import settings
from liono.common import getTickets
from liono.common import csvtohtml
from liono.logging import logger
import os.path,threading
#MAIN#
def main(pw):
    logger.log("==TE1 CaseManager UI ==")
    logger.log("User: {}".format(settings.uname))
    flag    = True
    # Get the assigned tickets based on cec user id / pw
    t       = threading.Thread(target = getTickets.jira, args=(settings.talosjira, flag, pw))
    t.start()
    try:
        t.join()
    except Exception as e:
        logger.log(e)
    # create the csv file to generate a html web template
    if settings.filedata is not None:
        csvtohtml.writedata(flag)
        csvtohtml.htmloutput(settings.htmlfname)
        fileExists  = os.path.exists(settings.htmlfname)
        exists      = ("The file, ", settings.htmlfname +",exists: {}".format(fileExists))
        logger.log(exists)
    else:
        logger.log("No file data in filedata variables from settings")
        logger.log("Or some other error in csv creation")
    # Get unassigned tickets in COG project
    #getTickets.unassigned(pw)
######################
# Run Main As Program
if __name__ == "__main__":
    main()