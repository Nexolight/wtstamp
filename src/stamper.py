import logging
import os
import json
import time
from datetime import datetime
from src import settings
from src.utils import Utils
from models.models import Workday,WorkdayJSONEncoder,WorkdayJSONDecoder

class Stamper():
    def __init__(self):
        self.l = logging.getLogger(__name__+"."+self.__class__.__name__)
        self.historydir = settings.get("history_data")
        
    
    def new(self):
        wd = Workday()
        ts = datetime.fromtimestamp(wd.start).strftime(settings.get("time_format"))
        self.updateWorktime(wd)
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
        self.updateWorktime(wd)
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
            self.updateWorktime(wd)
            wd.persist(self.historydir)
            self.l.info("Workday resumed!")
    
    def end(self):
        wd = Workday.loadLast(self.historydir)
        if(not wd):
            self.l.error("There's no workday started yet")
            return 
        for breaks in wd.breaks:
            if(breaks.get("start") and not breaks.get("end")):
                breaktime = datetime.fromtimestamp(breaks.get("start")).strftime(settings.get("time_format"))
                self.l.error("There's a break going on since "+breaktime)
                try:
                    uip = input("How many minutes? :")
                    now = time.time()
                    resumetime = breaks.get("start") + (int(uip) * 60)
                    if(resumetime > now):
                        resumetime = now - 60
                    breaks.update({"start":breaks.get("start"),"end":resumetime})
                    break
                except:
                    self.end()
        wd.end = time.time()
        self.updateWorktime(wd)
        wd.persist(self.historydir)
        self.l.info("Workday ended!")
        
    def updateWorktime(self, wd):
        stats = Utils.getWDStats(wd)
        self.l.debug("worktime: "+datetime.utcfromtimestamp(stats.get("worktime")).strftime("%Hh %Mm %Ss"))
        self.l.debug("breaktime: "+datetime.utcfromtimestamp(stats.get("breaktime")).strftime("%Hh %Mm %Ss"))   
    
    
        