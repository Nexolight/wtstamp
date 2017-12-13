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
        self.l.debug("worktime: "+datetime.utcfromtimestamp(stats.get("worktime")).strftime("%Hh %Mm %Ss"))
        self.l.debug("breaktime: "+datetime.utcfromtimestamp(stats.get("breaktime")).strftime("%Hh %Mm %Ss"))   
    
    def moveStart(self, seconds, ts=None, visualizer=None, noOffset=False):
        '''
        Normally this moves the time of the <Workday> (ts) forward or backward.
        When no ts is given, the last open (1st) or the last closed (2nd) <Workday> is used.
        When noOffset is used it will will add seconds to the begin of the used <Workday> instead.
        '''
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
        if(wd.end and newStart >= wd.end):
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
            
    def moveEnd(self, seconds, ts=None, visualizer=None, setDirect=False, setFromDaystart=False):
        '''
        Normally this moves the time of the <Workday> (ts) forward or backward.
        When no ts is given, the last closed <Workday> is used.
        When setDirect is used it will apply seconds like a full timestamp and when setFromDaystart
        is used it will apply seconds to the begin of the used <Workday>
        '''
        wd = Utils.evalEditDay(self.historydir,ts,noOpenDays=True)
        if(not wd):
            self.l.error("Unable to find the specified or last workday")
            return
        
        newEnd=0
        if(setFromDaystart == True):
            newEnd = datetime.strptime(datetime.fromtimestamp(wd.start).strftime("%d.%m.%Y"), "%d.%m.%Y").timestamp() + seconds
        elif(setDirect == True):
            newEnd = seconds
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
    
    def insert_workday(self, insertAt, ts, setDirect=False, visualizer=None):
        '''
        Normally this tries to insert a workday at the given timestamp with the given positive offset (ts).
        However, if setDirect is True it will use <ts> as explicit workday end.
        '''
        wd = Workday()
        wd.start = insertAt
        if(setDirect == True):
            wd.end = ts
        else:
            wd.end = wd.start+ts
        self.updateWorktime(wd)
        wd.persist(self.historydir,askoverride=True)
        self.l.info("New workday inserted at "+datetime.fromtimestamp(wd.start).strftime(settings.get("time_format")))
        if(visualizer):
            visualizer.day(wd.start)
            
    def insert_break(self, insertAt, breakStart, ts, setDirect=False, visualizer=None):
        '''
        Inserts a break into a given workday, starting from the given day and time, ending at the given "ts" (offset)
        when setDirect is True ts is not an offset but an explicit time.
        '''
        wd = Workday.loadDay(self.historydir,insertAt).get("workday")
        if(not wd):
            self.l.error("Unable to find the specified workday")
            return
        breakEnd=0
        if(setDirect == True):
            breakEnd=ts
        else:
            breakEnd=breakStart+ts
        for brk in wd.breaks:
            if(brk.get("end")):
                if(breakStart >= brk.get("start") and breakStart <= brk.get("end")):
                    self.l.error("REFUSED: Conflicting breaks. Requested start: "+datetime.fromtimestamp(breakStart).strftime(settings.get("time_format")))
                    if(visualizer):
                        visualizer.day(wd.start)
                    return
                elif(breakStart <= brk.get("start") and breakEnd >= brk.get("start")):
                    self.l.error("REFUSED: Conflicting breaks. Requested end: "+datetime.fromtimestamp(breakEnd).strftime(settings.get("time_format")))
                    if(visualizer):
                        visualizer.day(wd.start)
                    return
            else:     
                if(breakStart >= brk.get("start")):
                    self.l.error("REFUSED: There's a not closed break going on which conflicts with the requested start: "+datetime.fromtimestamp(breakStart).strftime(settings.get("time_format")))
                    if(visualizer):
                        visualizer.day(wd.start)
                    return
        if(not wd.end):# I don't want to take away the possibility but it's dangerous.
            uip = input("This workday has not yet ended! Inserting a break which takes longer\n\rthan a finished workday results in undefined behavior!\n\rThe requested break and minimum workday end would be: "+datetime.fromtimestamp(breakEnd).strftime(settings.get("time_format"))+".\n\rDo you want to continue? [N/y] :")
            if(uip.lower() != "y"):
                return;
        elif(wd.end <= breakEnd):
            self.l.error("REFUSED: Break would end later than the workday ends. Break would end at: "+datetime.fromtimestamp(breakEnd).strftime(settings.get("time_format")))
            if(visualizer):
                visualizer.day(wd.start)
            return
        wd.breaks.append({"start":breakStart,"end":breakStart+ts})
        self.updateWorktime(wd)
        wd.persist(self.historydir)
        self.l.info("New break inserted at workday "+datetime.fromtimestamp(wd.start).strftime(settings.get("date_simple_format"))+
                    ". Starts at: "+datetime.fromtimestamp(breakStart).strftime(settings.get("time_format"))+
                    ". Ends at: "+datetime.fromtimestamp(breakEnd).strftime(settings.get("time_format")))
        if(visualizer):
            visualizer.day(wd.start)
        
        
        