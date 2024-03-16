import os, sys, subprocess, time, re, threading
class CloudflareManager:
    __cloudfaredServerAndPid = {}
    __cloudfaredPid = []
    __prootPids = []
    logPathDir=""
    # logfiledict = {}
    logFiles = []
    if os.name == 'nt':
        binPath = r'C:\Program Files\cloudflare\bin'
        logPathDir = os.path.join(os.getenv("TEMP"),"cloudflare")
        if not os.path.exists(logPathDir):
            os.makedirs(logPathDir)
    if os.name == 'posix':
        if "/data/data/com.termux/files" in os.getcwd():
            binPath = "/data/data/com.termux/files/usr/bin"
            logPathDir = "/data/data/com.termux/files/home/cloudflare/log"
        else:
            binPath = "/usr/bin"
            logPathDir = "/home/cloudflare/log"
    @classmethod
    def generateLogFile(cls, serverKey):
        if f"log_{serverKey}.txt" not in cls.logFiles:
            return [True, f"log{serverKey}.txt"]
        else:
            return [False, "This port is already in use. Try another"]
    @classmethod
    def __runServer(cls, lhost: str, lport: int, logfilePath: str):
        if os.path.exists(logfilePath):
            os.remove(logfilePath) 
        if os.name == 'nt':
            os.chdir(cls.binPath)
            os.system(f".\cloudflared.exe -url {lhost}:{lport} --logfile {logfilePath} 2>{os.devnull}")
        elif os.name == 'posix':
            os.system(f"cloudflared -url {lhost}:{lport} --logfile {logfilePath} 2>{os.devnull}")
    @classmethod
    def __getPidOfServer(cls):
        validPid=None
        if os.name == 'nt':
            try:
                rawpids = subprocess.check_output("tasklist | findstr cloudflared", shell=True)
                rawpids = rawpids.decode("utf-8")
                rawpids = re.findall(r"cloudflared\.exe\s+(\d+)\s+Console", rawpids)
            except subprocess.CalledProcessError as e:
                sys.stderr.write(str(e)+"\n")
                sys.stderr.write("Unable to get the pid of the this instance of cloudflared")
                # exit(1)
                return None
        if os.name == 'posix':
            try:
                rawpids1 = subprocess.check_output("pgrep -af cloudflared | awk '{print $1}'", shell=True)
                rawpids2 = subprocess.check_output("pgrep -af cloudflared | awk '{print $1}'", shell=True)
                rawpids1 = rawpids1.decode("utf-8")
                rawpids2 = rawpids2.decode("utf-8")
                try:
                    rawpids1 = rawpids1.split("\n")
                    rawpids2 = rawpids2.split("\n")
                except:
                    pass
                rawpids = [element for element in rawpids1 if element in rawpids2 and (element != '' and not str(element).isspace())]
                try:
                    pidOfproot = subprocess.check_output("pgrep -af proot | awk '{print $1}'", shell=True).decode("utf-8").split("\n")
                    pidOfproot = [i for i in pidOfproot if i is not None and (i!='' and not str(i).isspace())]
                    if len(pidOfproot) > 0:
                        for pi in pidOfproot:
                            if pi not in cls.__prootPids:
                                cls.__prootPids.append(pi)
                except:
                    pass
            except subprocess.CalledProcessError as e:
                sys.stderr.write(str(e) + "\n")
                sys.stderr.write("Unable to get the pid of the this instance of cloudflared")
                exit(1)
        currentPidListLen = len(cls.__cloudfaredPid)
        if len(rawpids) > 0:
            for i in rawpids:
                if i not in cls.__cloudfaredPid:
                    cls.__cloudfaredPid.append(i)
        if len(cls.__cloudfaredPid) > currentPidListLen:
            return cls.__cloudfaredPid[-1]
        return validPid
    @staticmethod
    def startCloudflareServer(lhost: str, lport: int):
        __key = f"{lhost}:{lport}"
        __fileKey = f"{lhost}_{lport}"
        logfilePath = CloudflareManager.generateLogFile(__fileKey)
        if logfilePath[0] == True:
            logfilePath = os.path.join(CloudflareManager.logPathDir, logfilePath[1])
        else:
            sys.stderr.write(logfilePath[0])
            return logfilePath
        try:
            updateCurrentPids = CloudflareManager.__getPidOfServer()
        except:
            pass
        if CloudflareManager.__cloudfaredServerAndPid.get(__key) is not None:
            if str(CloudflareManager.__cloudfaredServerAndPid.get(__key)) == str(updateCurrentPids):
                return [False, "This server is already in use! Try again with different lhost and lport values!!"]
        print("Going to start server")
        threading.Thread(target=CloudflareManager.__runServer, args=[lhost, lport, logfilePath]).start()
        print("Server running")
        time.sleep(10)
        currentPid = CloudflareManager.__getPidOfServer()
        CloudflareManager.__cloudfaredServerAndPid[__key] = currentPid
        CloudflareManager.logFiles.append(f"log{lhost}_{lport}.txt")
        link=None
        while True:
            print("\n\nTrying to read the link\n\n")
            with open(logfilePath, "r") as logfile:
                content = logfile.read()
                logfile.close()
                if len(content) > 0:
                    link = re.findall(r'https://[-0-9a-z]*\.trycloudflare.com', content)
                    if link:
                        break
                    else:
                        continue
        return link
@staticmethod
def killServer(lhost, lport):
    __key = f"{lhost}:{lport}"
    if CloudflareManager.__cloudfaredServerAndPid.get(__key) is not None:
        pidToKill = CloudflareManager.__cloudfaredServerAndPid[__key]
        try:
            os.kill(pidToKill, 9)
        except OSError:
            sys.stderr.write(f"Unable to kill Cloudflare pid: {pidToKill}. Kill it manually\n")
            return [False, f"Unable to kill cloudflare pid: {pidToKill}. Kill it manually\n"]
        CloudflareManager.__cloudfaredServerAndPid.pop(__key)
        CloudflareManager.__cloudfaredPid.remove(pidToKill)
        try:
            CloudflareManager.logFiles.remove(os.path.join(CloudflareManager.logPathDir,f"log{lhost}_{lport}.txt"))
        except:
            pass
        return [True, f"Successfully killed cloudflare pid: {pidToKill}"]