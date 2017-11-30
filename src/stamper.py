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
        wd = Workday.loadLast(self.historydir).get("workday")
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
        wd = Workday.loadLast(self.historydir).get("workday")
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
        wd = Workday.loadLast(self.historydir).get("workday")
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
        self.l.debug("worktime: "+datetime.fromtimestamp(stats.get("worktime")).strftime("%Hh %Mm %Ss"))
        self.l.debug("breaktime: "+datetime.fromtimestamp(stats.get("breaktime")).strftime("%Hh %Mm %Ss"))   
    
    def moveStart(self, seconds, ts=None, visualizer=None, noOffset=False):
        wd = Utils.evalEditDay(self.historydir,ts)
        if(not wd):
            self.l.error("Unable to find the specified, currently open or last workday")
            return
        
        newStart=0
        if(noOffset == True):
            newStart = datetime.strptime(datetime.fromtimestamp(wd.start).strftime("%d.%m.%Y"), "%d.%m.%Y").timestamp() + seconds
        else:
            newStart = wd.start + seconds
        
        oldStartDayTS = datetime.strptime(datetime.fromtimestamp(wd.start).strftime("%d.%m.%Y"), "%d.%m.%Y").timestamp()
        self.l.info("Using "+datetime.fromtimestamp(wd.start).strftime(settings.get("time_format")))
        if(visualizer):
            visualizer.day(wd.start)
        if(newStart <= oldStartDayTS):
            self.l.error("REFUSED: The new date would end up beeing from the previous day which isn't allowed")
            return
        if(newStart >= wd.end):
            self.l.error("REFUSED: The new date can't be more recent than the end of this workday")
            return
        for brk in wd.breaks:
            if(brk.start <= newStart):
                self.l.error("REFUSED: The new date can't be more recent than the first started break of this workday")
                return
        self.l.info("Changed to "+datetime.fromtimestamp(newStart).strftime(settings.get("time_format")))
        wd.start = newStart
        wd.persist(self.historydir);
        if(visualizer):
            visualizer.day(newStart)
            
    def moveEnd(self, seconds, ts=None, visualizer=None, noOffset=False):
        wd = Utils.evalEditDay(self.historydir,ts)
        if(not wd):
            self.l.error("Unable to find the specified, currently open or last workday")
            return
        
        newEnd=0
        if(noOffset == True):
            newEnd = datetime.strptime(datetime.fromtimestamp(wd.end).strftime("%d.%m.%Y"), "%d.%m.%Y").timestamp() + seconds
        else:
            newEnd = wd.end + seconds
        
        if(newEnd <= wd.start):
            self.l.error("REFUSED: The new date can't be less recent than the start of this workday")
            return
        for brk in wd.breaks:
            if(brk.end >= newEnd):
                self.l.error("REFUSED: The new date can't be less recent than the last ended break of this workday")
                return
        self.l.info("Using "+datetime.fromtimestamp(wd.end).strftime(settings.get("time_format")))
        if(visualizer):
            visualizer.day(wd.start)
        self.l.info("Changed to "+datetime.fromtimestamp(newEnd).strftime(settings.get("time_format")))
        wd.end = newEnd
        wd.persist(self.historydir);
        if(visualizer):
            visualizer.day(wd.start)
                
        
        
        