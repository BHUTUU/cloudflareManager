import os, sys, subprocess, time, re
class CloudflareManager:
    __cloudfaredPid = []
    __prootPids = []
    if os.name == 'nt':
        binPath = "C:\\Program Files\\cloudflare\\bin"
    if os.name == 'posix':
        if "/data/data/com.termux/files" in os.getcwd():
            binPath = "/data/data/com.termux/files/usr/bin"
        else:
            binPath = "/usr/bin"
    @classmethod
    def __runServer(cls, lhost: str, lport: int, logfilePath: str):
        if os.name == 'nt':
            subprocess.Popen(f"{cls.binPath}\\cloudflared.exe -url {lhost}:{lport} --logfile {logfilePath}", shell=True)
        elif os.name == 'posix':
            subprocess.Popen(f"{cls.binPath}/cloudflared -url {lhost}:{lport} --logfile {logfilePath}", shell=True)
    @classmethod
    def __getPidOfServer(cls):
        validPid=None
        if os.name == 'nt':
            try:
                rawpids = subprocess.check_output("tasklist | findstr cloudflared", shell=True)
                rawpids = rawpids.decode("utf-8")
                rawpids = re.findall(r"cloudflared\.exe\s+(\d+)\s+Console")
            except subprocess.CalledProcessError as e:
                sys.stderr.write(e)
                sys.stderr.write("Unable to get the pid of the this instance of cloudflared")
                exit(1)
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
                sys.stderr.write(e)
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

            