__version__ = "1.0.1"


import threading
class Runner(threading.Thread):
    from subprocess import Popen as __Popen
    from time import sleep as __sleep
    from sys import executable as __executable
    from os import stat as __stat
    from threading import Thread as __Thread
    import customisedLogs as __customisedLogs
    def __init__(self, toRun:dict[str, list[str]], toCheck:list[str], reCheckInterval:int=1):
        """
        Initialise the Runner with appropriate parameters and use the start() method to start the process
        :param toRun: dictionary with filenames to run as the keys and list of all arguments to pass as the value
        :param toCheck: list of all the filenames to check for updates
        :param reCheckInterval: count in seconds to wait for update check
        """
        self.__Thread.__init__(self)
        self.logger = self.__customisedLogs.Manager()
        self.programsToRun = toRun
        self.programsToCheck = toCheck
        self.currentProcesses:list[Runner.__Popen] = []
        self.reCheckInterval:float = reCheckInterval
        self.lastFileStat = self.fetchFileStats()
        self.startPrograms()


    def run(self):
        """
        Overriding run from threading.Thread
        Infinite Loop waiting for file updates and re-run the programs if updates found
        :return:
        """
        while True:
            if self.checkForUpdates():
                self.startPrograms()
            self.__sleep(self.reCheckInterval)


    def fetchFileStats(self)->dict[str, float]:
        """
        Checks current file state
        Returns a list containing tuples containing each file and its last modified state
        If a to-be-checked file gets added, or goes missing, it is treated as a file update
        :return:
        """
        tempStats:dict[str, float] = {}
        for filename in self.programsToCheck:
            try:
                tempStats[filename] = self.__stat(filename).st_mtime
            except: ## file is not present
                tempStats[filename] = 0
        return tempStats


    def checkForUpdates(self)->bool:
        """
        Checks if current file state matches old known state
        Returns a boolean if current received file state differs from the last known state
        :return:
        """
        fileStat = self.fetchFileStats()
        if self.lastFileStat != fileStat:
            changes = []
            for file in fileStat:
                if fileStat[file] != self.lastFileStat[file]:
                    changes.append(file)
            self.logger.success("FILE CHANGED", "\n".join(changes))
            self.lastFileStat = fileStat
            return True
        else:
            return False


    def startPrograms(self):
        """
        Respawns processes
        Kills last running processes if any and then respawn newer processes for each file to be run
        :return:
        """
        temp = self.currentProcesses.copy()
        if temp:
            self.logger.success("PROCESS" "Killing previous processes")
        for _process in temp:
            if _process and not _process.poll():
                _process.kill()
                _process.wait()
                self.currentProcesses.remove(_process)
        for program in self.programsToRun:
            self.currentProcesses.append(self.__Popen([self.__executable, program]+self.programsToRun[program]))
            self.logger.success("PROCESS" "Started new process")
