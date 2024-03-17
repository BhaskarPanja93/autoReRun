# customisedLogs v1.1.0

```pip install autoReRun --upgrade```


###### <br>A simple program to automatically kill running process(es) and re-spawn new process(es) for the runnable files everytime some specified file(s) get modified (or deleted or created). For example, Automatically re-starting any server when the server file(s) is modified.

<br>To install: 
```
pip install autoReRun --upgrade
pip3 install autoReRun --upgrade
python -m pip install autoReRun --upgrade
python3 -m pip install autoReRun --upgrade
```


#### <br><br>Using this program is as simple as:
```
from autoReRun import Runner as updateRunner

toRun = {
    "server1.py":["-p 5000", "-h 0.0.0.0"], # file A to run
    "server2.py":["-p 6000"], # file B to run
         }
         
toCheck = [
    "server1.toml",  # file X to check for updates
    "server2.toml" # file Y to check for updates
           ]
           
# start the process
updateRunner(toRun=toRun, toCheck=toCheck).start() 
```

### Future implementations:
* Only limited to python files, make it work with any other file type.
* Way to turn off debugger.


###### <br>This project is always open to suggestions and feature requests.