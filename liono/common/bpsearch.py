from liono.common import settings
settings.init()
import git,os,sys,re,time,shutil,sys,threading
from git import RemoteProgress

# search for the sig in disabled/retired locations
def retired(sig):
    os.chdir(os.path.expanduser('~'))
    N   = 10
    cwd = os.getcwd()
    print("\n==Retired/Disabled BP Sig==")
    settings.bpres.append("==Retired/Disabled==")
    if os.path.exists(cwd+"/BP-Sigs/ATTIC/Signatures/windows"):
        try:
            os.chdir(cwd+"/BP-Sigs/ATTIC/Signatures/windows")
        except:
            print("Directory, "+cwd+"/BP-Sigs/ATTIC/Signatures/windows does not exist")
    elif os.path.exists(cwd+"/BP-Sigs/apde-signatures/ATTIC/Signatures/windows"):
        try:
            os.chdir(cwd+"/BP-Sigs/apde-signatures/ATTIC/Signatures/windows")
        except:
            print("Directory,"+cwd+"/BP-Sigs/apde-signatures/ATTIC/Signatures/windows does not exist")
    else:
        pass
    cwd = os.getcwd()
    if "ATTIC" in cwd or "attic" in cwd: # verify we are looking for deactivated sigs
        for file in os.listdir():
            if os.path.isdir(file):
                pass
            else:
                if sig in open(file).read():
                    found = file
                    with open(found, 'r') as f:
                        for i in range(N):
                            line = f.__next__()
                            strp = ''.join(line.splitlines())
                            if "name" in strp:
                                name = re.sub("name:+", "", strp)
                                name.strip()
                                settings.bp.update({"name": name})
                            if "id" in strp:
                                bpid = re.sub("id:+", "", strp)
                                bpid.strip()
                                settings.bp.update({"id": bpid})
                            if "revision" in strp:
                                rev = re.sub("revision:+", "", strp)
                                rev.strip()
                                settings.bp.update({"rev": rev})
                            settings.bp.update({"active": False})
                            print(strp)
                            settings.bpres.append(strp)
                        settings.bpres.append("=====================")
                    f.close
                    #print("Filename: {}".format(found))
                    #print("==========================================")

# search all dirs in BP sigs
def findrev(sig):
    found   = ""
    N       = 10
    home    = os.path.expanduser("~")
    print("\n==ACTIVE BP Sig==")
    settings.bpres.append("==Active BP Sigs==")
    # search every directory and file for a match in BP-Sigs
    for dirpath,dirnames,files in os.walk(home+'/BP-Sigs/apde-signatures/Signatures/enterprise/'):
        for file in files:
            if file.endswith('.sig'):
                fullpath = os.path.join(dirpath, file)
                with open(fullpath, 'r') as f:
                    for line in f:
                        if sig in line:
                            found = fullpath
                            with open(found, 'r') as f2:
                                for i in range(N):
                                    line = f2.__next__()
                                    strp = ''.join(line.splitlines())
                                    if "name" in strp:
                                        name = re.sub("name:+", "", strp)
                                        name.strip()
                                        settings.bp.update({"name": name})
                                    if "id" in strp:
                                        bpid = re.sub("id:+", "", strp)
                                        bpid.strip()
                                        settings.bp.update({"id": bpid})
                                    if "revision" in strp:
                                        rev = re.sub("revision:+", "", strp)
                                        rev.strip()
                                        settings.bp.update({"rev": rev})
                                    settings.bp.update({"active": True})
                                    # Print the first 7 lines about the signature
                                    print(strp)
                                    settings.bpres.append(strp)
                                settings.bpres.append("======================")
                                # Print the filename and location of the sig
                                #print("Filename: {}".format(found))
                                print("==========================================")
                                break
                            f2.close()
                f.close()

# set the path and sig search for linux
def searchlinux(platform,sig):
    os.chdir(os.path.expanduser('~'))
    N   = 10
    cwd = os.getcwd()
    os.chdir(cwd+platform)
    # search each file for a match
    for file in os.listdir():
        if os.path.isdir(file):
            pass
        else:
            if sig in open(file).read():
                found = file
                with open(found, 'r') as f:
                    for i in range(N):
                        line = f.__next__()
                        strp = ''.join(line.splitlines())
                        if "name" in strp:
                            name = re.sub("name:+", "", strp)
                            name.strip()
                            settings.bp.update({"name": name})
                        if "id" in strp:
                            bpid = re.sub("id:+", "", strp)
                            bpid.strip()
                            settings.bp.update({"id": bpid})
                        if "revision" in strp:
                            rev = re.sub("revision:+", "", strp)
                            rev.strip()
                            settings.bp.update({"rev": rev})
                        settings.bp.update({"active": True})
                        # Print the first 7 lines about the signature
                        print(strp)
                        settings.bpres.append(strp)
                    settings.bpres.append("===================================")
                    # Print the filename and location of the sig
                    #print("Filename: {}".format(found))
                    print("==========================================")
                    break
                f.close()

# check the linux and macos folders for sigs
def checklinux(sig):
    cwd     = os.getcwd()
    mac     = "/BP-Sigs/apde-signatures/Signatures/enterprise/common/macos/"
    linux   = "/BP-Sigs/apde-signatures/Signatures/enterprise/common/linux/"
    linux   = "/BP-Sigs/apde-signatures/Signatures/enterprise/common/linux/"
    print("\n==MacOS & Linux==")
    settings.bpres.append("==MacOS & Linux==")
    searchlinux(mac, sig)
    searchlinux(linux,sig)

#check if the gitlab repo is accessible and valid
def isvalid(path):
    try:
        _ = git.Repo.init(path)
        return True
    except git.InvalidGitRepositoryError:
        return False

# download apde/cloud signature git code
def bpdownload():
    os.chdir(os.path.expanduser('~'))
    cwd         = os.getcwd()
    folder_path = cwd + '/BP-Sigs'
    res         = None
    #verify that the repo is valid and we have login access
    valid       = False
    valid       = isvalid(settings.pkg)               # if git repo is accessible return true
    #print(valid)
    if os.path.exists(folder_path) is True:           # if BP sig dir already exists check timestamp
        lastmodtime = os.stat(folder_path).st_mtime
        now         = time.time()
        timediff    = int(now) - int(lastmodtime)
        if timediff >= 86400 and valid is True:        # if timestamp is older than 24 hours and repo is accessible,download updated sigs
            print("BP Signatures older than 24 hours. New file download in process.....\n\n")
            shutil.rmtree(folder_path)
            try:
                os.makedirs(folder_path)
                git.Git(folder_path).clone(settings.pkg)
                res = ("Updated BP Sigs Successful!!")
                print(res)
                return res
            except Exception as e:
                res = ("Download error: ", e)
                print(res)
                return(res)
        else:
            res = ("BP Signatures downloaded less than 24 hours ago.")
            print(res)
            return res
    else: # no previous signature download located so download new sigs
        if valid is True:                           # if git repo is accessible and not BP-Sig dir is under the user home dir download sigs
            print("BP Signature file download in process.....\n\n")
            try:
                # if BP sigs does not exist create the dir under the user home folder
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    git.Git(folder_path).clone(settings.pkg)
                else:
                    git.Git(folder_path).clone(settings.pkg)
                res = "Download of BP Sigs Successful!"
                print(res)
                return(res)
            except Exception as e:
                print(e)
                err = ('Download error - BP Sigs')
                print(err)
                return err
        else:
            err = ("Error accessing the Git Repo"+settings.repo)
            print(err)
            return err

# MAIN
def bp(sig):
    threads = []
    sig.strip()                                                             # removed trailing spaces or return chars
    settings.bp.update({"usrstrng": sig})                                   # add the user sig/qry to settings variable
    t1 = threading.Thread(target=findrev, args=(sig,))                      # check for BP id in any of the BP sigs
    t2 = threading.Thread(target=checklinux, args=(sig,))                   # check if BP id is linux/osx
    t3 = threading.Thread(target=retired, args=(sig,))                      # cehck if BP id is retired
    threads.extend([t1,t2,t3])
    for t in threads:
        t.start()
        t.join()
