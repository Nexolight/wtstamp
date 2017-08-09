from datetime import datetime
from src import settings
import time

class Utils:
    
    def __init__(self):
        pass
    
    @staticmethod
    def getWDStats(wd):
        '''
        Returns information about the workday in a dictionary
        {
            worktime:<utc_seconds>
            breaktime:<utc_seconds>
        }
        '''
        last_stamp=time.time()
        if(wd.end):
           last_stamp=wd.end
           
        breaktime=0 
        for breaks in wd.breaks:
            if(breaks.get("start") and breaks.get("end")):
                breaktime+=breaks.get("end")-breaks.get("start")
            elif(breaks.get("start") and not breaks.get("end") and not wd.end):
                last_stamp=breaks.get("start")
        worktime=last_stamp-wd.start
        worktime-=breaktime
        return {
            "worktime":worktime,
            "breaktime":breaktime
        }
        
    @staticmethod
    def pb(rawstring):
        '''
        Returns text decorated with border
        '''
        out=""
        if rawstring:
            while len(rawstring) > 0:
                out+="| "
                fill=""
                end=len(rawstring)
                if(end > settings.get("border_width")-4):
                    end=settings.get("border_width")-4
                elif(end < settings.get("border_width")-4):
                    fill=" "*((settings.get("border_width")-4)-end)
                out+=rawstring[0:end]+fill+" |\n"
                rawstring=rawstring[end:len(rawstring)+1]
        return out
    
    @staticmethod
    def pbn():
        '''
        Returns a newline with decorated border
        '''
        return "|"+(" "*(settings.get("border_width")-2))+"|\n"
    
    @staticmethod
    def pbdiv():
        '''
        Returns a dividing line
        '''
        return "|"+("-"*(settings.get("border_width")-2))+"|\n"
        