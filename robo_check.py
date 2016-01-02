# a script to scrape robo-panda wiki
# Ryan 10-14-2015

import sys, os
from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.QtWebKit import *  
from lxml import html 
import time
import re
import datetime
import pickle

# javascript scraping class from: https://impythonist.wordpress.com/2015/01/06/ultimate-guide-for-scraping-javascript-rendered-web-pages/
class Render(QWebPage):  
  def __init__(self, url):  
    self.app = QApplication(sys.argv)  
    QWebPage.__init__(self)  
    self.loadFinished.connect(self._loadFinished)  
    self.mainFrame().load(QUrl(url))  
    self.app.exec_()  
  
  def _loadFinished(self, result):  
    self.frame = self.mainFrame()  
    self.app.quit() 

start_t = time.time()
print("started reconstructing the html from robo-panda/")
robo_panda = 'http://robo-panda/'
render_instance = Render(robo_panda) # this is a slow step that reconstructs HTML using javascript
result = render_instance.frame.toHtml()
print("and...finished  " + "elapsed time: {0:.2f}".format((time.time() - start_t)))

print("searching the html...")
matches = re.findall(r'<div class="about_labber">\n<div class="name ng-binding" ng-style="l.name_style">*.+</div>', result)

names = []
for this_case in matches:
    this_name = re.search('ng-style="l.name_style">(.+?)</div>', this_case).group(1)
    names.append(this_name)


# Check these names against most recent data
print("")
print("Comparing to last view...")
data_path = '/Users/ryan/Documents/ryan non-work/robo_panda_data/'
files = os.listdir(data_path)
files.sort()
last_data = pickle.load(open(data_path + files[-1], "rb"))
old_names = last_data['names']
last_change_date = last_data['date_human']
#old_names = old_names[0:-5] #DEBUG
#names = names[5::] # DEBUG

# Report on current status
print("The employees currently are:\n")
for name in names: print(name)
print("\nCurrently there are {0} employees on robo-panda/\n".format(len(names)))

# build the changes summary
change_summary = ""
if(set(names) == set(old_names)):
    change_summary = change_summary + "No Change"
    changes = False
else: 
    new_people = set(names) - set(old_names)
    missing_people = set(old_names) - set(names)
    if(new_people): change_summary = change_summary + "\n{0} new people: {1}".format(len(new_people), new_people) 
    if(missing_people): change_summary = change_summary + "\n{0} missing people: {1}".format(len(missing_people), missing_people)
    changes = True
print("Since {0} the differences are:".format(last_change_date))
print(change_summary)
print("")
if(changes):
    # Save today's data as a pickled dictionary
    datenow = datetime.datetime.now()
    names_dict = {
        'names' : names,
        'date' : datenow,
        'date_human' : str(datenow),
        'total' : len(set(names)), 
        'changes' : change_summary
    }       

    data_path = '/Users/ryan/Documents/ryan non-work/robo_panda_data/'  

    # Prepare to save new data
    filename = "robo_scrape_" + str(datenow)
    filename = re.sub(r'\s+', "-", filename)
    filename = re.sub(r'\.', "-", filename)
    filename = re.sub(r':', "-", filename)
    filename = data_path + filename +  ".p"
    pickle.dump(names_dict, open( filename, "wb" ), protocol=2) # protocol 2 is backwards-compatible with Python2
    print("Saved latest robo_scrape to {0}".format(filename))
else:
    print("Did not save redundant data.")

