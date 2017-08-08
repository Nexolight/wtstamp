import logging
import os
import json
import time
from datetime import datetime
from src import settings
from models.models import Workday,WorkdayJSONEncoder,WorkdayJSONDecoder

class Stamper():
    def __init__(self):
        self.l = logging.getLogger(__name__+"."+self.__class__.__name__)
        self.historydir = os.path.join(settings.get("application_data"),"history")
        
    
    def new(self):
        wd = Workday()
        ts = datetime.fromtimestamp(wd.start).strftime(settings.get("time_format"))
        wd.persist(self.historydir,askoverride=True)
        self.l.info("New workday started at "+ts)
    
    def pause(self):
        wd = Workday.loadLast(self.historydir)
        for breaks in wd.breaks:
            #disallow break when another break is going on
            if(breaks.get("start") and not breaks.get("end")):
                breaktime = datetime.fromtimestamp(breaks.get("start")).strftime(settings.get("time_format"))
                self.l.error("You need to stop the break started since "+breaktime+" first")
                return
        wd.breaks.append({"start":time.time(),"end":None})
        wd.persist(self.historydir)
        self.l.info("Workday paused!")
    
    def resume(self):
        wd = Workday.loadLast(self.historydir)
        found=False
        for breaks in wd.breaks:
            if(breaks.get("start") and not breaks.get("end")):
                breaks.update({"start":breaks.get("start"),"end":time.time()})
                found=True
                break
        if(not found):
            self.l.error("There's no break going on")
        else:
            wd.persist(self.historydir)
            self.l.info("Workday resumed!")
    
    def end(self):
        wd = Workday.loadLast(self.historydir)
        for breaks in wd.breaks:
            if(breaks.get("start") and not breaks.get("end")):
                breaktime = datetime.fromtimestamp(breaks.get("start")).strftime(settings.get("time_format"))
                self.l.error("There's a break going on since "+breaktime)
                try:
                    uip = input("How many minutes? ")
                    now = time.time()
                    resumetime = breaks.get("start") + (int(uip) * 60)
                    if(resumetime > now):
                        resumetime = now - 60
                    breaks.update({"start":breaks.get("start"),"end":resumetime})
                    break
                except:
                    self.end()
        wd.end = time.time()
        wd.persist(self.historydir)
        self.l.info("Workday ended!")
        

            
    
    
        