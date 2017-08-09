import logging
import os
from datetime import datetime
from src import settings
from src.utils import Utils
from models.models import Workday

class Visualizer():
    def __init__(self):
        self.l = logging.getLogger(__name__+"."+self.__class__.__name__)
        pass
    
    def day(self):
        #We want to know the last active workday
        lastwd = Workday.loadLast(os.path.join(settings.get("application_data"),"history"))
        info=""
        curwd = None
        curbreak = None
        stats = None
        if(lastwd):
            curwd=datetime.fromtimestamp(lastwd.start).strftime(settings.get("time_format"))
            stats=Utils.getWDStats(lastwd) #datetime.utcfromtimestamp(stats.get("worktime")).strftime("%Hh %Mm %Ss")
            #print(lastwd.breaks)
            for breaks in lastwd.breaks:
                if(breaks.get("start") and not breaks.get("end")):
                    curbreak=datetime.fromtimestamp(breaks.get("start")).strftime(settings.get("time_format"))
                    break
        info+=Utils.pbn()
        if(curwd):
            info+=Utils.pb("active workday >> "+curwd)
        if(curbreak):
            info+=Utils.pb("break since    >> "+curbreak)
        else:
            info+=Utils.pb("break since    >> currently working")
        if(stats):
            info+=Utils.pbn()
            info+=Utils.pb("worktime       >> "+datetime.utcfromtimestamp(stats.get("worktime")).strftime("%Hh %Mm %Ss"))
            info+=Utils.pb("breaktime      >> "+datetime.utcfromtimestamp(stats.get("breaktime")).strftime("%Hh %Mm %Ss"))
        info+="\n"
        print(info)
    
    def saldo(self):
        self.l.info("Generating saldo visualization...")
    
    def month(self):
        self.l.info("Generating month visualization...")
    
    def week(self):
        self.l.info("Generating week visualization...")
    
    def last(self):
        self.l.info("Generating visualization from last closed workday...")
    
    def open(self):
        self.l.info("Generating visualization from currently open workday...")
    