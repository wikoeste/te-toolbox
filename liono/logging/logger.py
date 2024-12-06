import logging, os

def log(msg):
    homedir = os.path.expanduser("~")      # write to users home directory
    fname = 'te1-webapp.log'               # file name of the log
    fmt = '%(asctime)s:%(name)s:%(levelname)s - %(message)s' # formate of the timestamps
    logging.basicConfig(filename=homedir + "/" + fname, format=fmt) # configuration complete for logging
    logging.error(msg)