__version__ = "1.3.0"
__packagename__ = "autorerun"


def updatePackage():
    from time import sleep
    from json import loads
    import http.client
    print(f"Checking updates for Package {__packagename__}")
    try:
        host = "pypi.org"
        conn = http.client.HTTPSConnection(host, 443)
        conn.request("GET", f"/pypi/{__packagename__}/json")
        data = loads(conn.getresponse().read())
        latest = data['info']['version']
        if latest != __version__:
            try:
                import subprocess
                from pip._internal.utils.entrypoints import (
                    get_best_invocation_for_this_pip,
                    get_best_invocation_for_this_python,
                )
                from pip._internal.utils.compat import WINDOWS
                if WINDOWS:
                    pip_cmd = f"{get_best_invocation_for_this_python()} -m pip"
                else:
                    pip_cmd = get_best_invocation_for_this_pip()
                subprocess.run(f"{pip_cmd} install {__packagename__} --upgrade")
                print(f"\nUpdated package {__packagename__} v{__version__} to v{latest}\nPlease restart the program for changes to take effect")
                sleep(3)
            except:
                print(f"\nFailed to update package {__packagename__} v{__version__} (Latest: v{latest})\nPlease consider using pip install {__packagename__} --upgrade")
                sleep(3)
        else:
            print(f"Package {__packagename__} already the latest version")
    except:
        print(f"Ignoring version check for {__packagename__} (Failed)")


class Imports:
    from threading import Thread
    from subprocess import Popen
    from time import sleep
    from sys import executable
    from os import stat
    from customisedLogs import CustomisedLogs


class AutoReRun(Imports.Thread):
    def __init__(self, toRun:dict[str, list[str]], toCheck:list[str], reCheckInterval:int=1, logOnTerminal:bool=True):
        """
        Initialise the Runner with appropriate parameters to start the process
        :param toRun: dictionary with filenames to run as the keys and list of all arguments to pass as the value
        :param toCheck: list of all the filenames to check for updates
        :param reCheckInterval: count in seconds to wait for update checks
        """
        Imports.Thread.__init__(self)
        self.__logger = Imports.CustomisedLogs() if logOnTerminal else None
        self.__programsToRun = toRun
        self.__programsToCheck = toCheck
        self.__currentProcesses:list[Imports.Popen] = []
        self.__reCheckInterval:float = reCheckInterval
        self.__lastFileStat = self.__fetchFileStats()
        self.__startPrograms()
        self.start()


    def run(self):
        """
        Overriding run from threading.Thread
        Infinite Loop waiting for file updates and re-run the programs if updates found
        :return:
        """
        while True:
            if self.__checkForUpdates():
                self.__startPrograms()
            Imports.sleep(self.__reCheckInterval)


    def __fetchFileStats(self)->dict[str, float]:
        """
        Checks current file state
        Returns a list containing tuples containing each file and its last modified state
        If a to-be-checked file gets added, or goes missing, it is treated as a file update
        :return:
        """
        tempStats:dict[str, float] = {}
        for filename in self.__programsToCheck:
            try:
                tempStats[filename] = Imports.stat(filename).st_mtime
            except: ## file is not present
                tempStats[filename] = 0
        return tempStats


    def __checkForUpdates(self)->bool:
        """
        Returns a boolean if current received file state differs from the last known state
        :return:
        """
        fileStat = self.__fetchFileStats()
        if self.__lastFileStat != fileStat:
            changes = []
            for file in fileStat:
                if fileStat[file] != self.__lastFileStat[file]:
                    changes.append(file)
            self.__logger.log(self.__logger.Colors.light_blue_800, "RERUN-FILE-CHANGED", "\n".join(changes))
            self.__lastFileStat = fileStat
            return True
        else:
            return False


    def __checkProgramHealth(self, process:Imports.Popen, program:str):
        """
        Wait for process end and cleanup
        :param process: The process to check
        :param program: program path
        :return:
        """
        process.wait()
        self.__logger.log(self.__logger.Colors.grey_800, "RERUN-FINISH", program, "ended execution")
        if process in self.__currentProcesses: self.__currentProcesses.remove(process)


    def __startPrograms(self):
        """
        Respawns processes
        Kills last running processes if any and respawn new processes for each file to be run
        :return:
        """
        temp = self.__currentProcesses.copy()
        if temp:
            self.__logger.log(self.__logger.Colors.red_800, "RERUN-OLD", "Killing old processes")
        for _process in temp:
            while _process in self.__currentProcesses or _process.poll() is None:
                _process.kill()
        for program in self.__programsToRun:
            _process = Imports.Popen([Imports.executable, program] + self.__programsToRun[program])
            Imports.Thread(target=self.__checkProgramHealth, args=(_process, program,)).start()
            self.__currentProcesses.append(_process)
            self.__logger.log(self.__logger.Colors.green_800, "RERUN-NEW", "Started new process")
