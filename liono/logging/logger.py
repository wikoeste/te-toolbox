from liono.common import settings
import logging, os  # first of all import the module

def log():
    # write to users home directory
    homedir = os.path.expanduser("~")
    #print(homedir)
    fname = 'te1_audit.log'
    fmt = '%(asctime)s:%(name)s:%(levelname)s - %(message)s'
    logging.basicConfig(filename=homedir + "/" + fname, format=fmt)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)