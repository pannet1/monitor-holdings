## Installations
[python 3.9](https://www.python.org/downloads/release/python-390/) or greater
[git bash](https://git-scm.com/downloads) to clone this git repo and keep it updated

## Setup
1. create a new virtualenv in the location `C:\ecomsense\py\venv` 
2. activate the virtualenv
3. git clone this repo with `git clone https://github.com/pannet1/monitor-holdings` 
4. `cd monitor-holdings`
5. `pip install -r requirements.txt`
6. copy the sample `bypass.yaml` to `C:\ecomsense\py` and make the necessary changes
7. create shortcut links for the bat files to the desktop for easy access.

That's all

## Starting up 
You just need to double click on the start algo.bat icon on the desktop and python will start monitoring your holdings.

## Note
There is a settings.yaml file from which you can change the percentage in case you wanted to change it in future.
whenever you run the program, it will generate the list of stocks it is going to monitor for the day based on the rule set.




