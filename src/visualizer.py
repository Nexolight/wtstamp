import logging
import os
import time
from datetime import datetime
from src import settings
from src.utils import Utils
from models.models import Workday

class Visualizer():
    def __init__(self):
        self.l = logging.getLogger(__name__+"."+self.__class__.__name__)
        pass
    
    def day(self):
        '''
        Print infos about the ongoing workday
        '''
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
        else:
            info+=Utils.pb("No active workday")
        if(curwd and curbreak):
            info+=Utils.pb("break since    >> "+curbreak)
        elif(curwd and not curbreak):
            info+=Utils.pb("break since    >> currently working")
        if(stats):
            info+=Utils.pbn()
            info+=Utils.pb("worktime       >> "+datetime.utcfromtimestamp(stats.get("worktime")).strftime("%Hh %Mm %Ss"))
            info+=Utils.pb("breaktime      >> "+datetime.utcfromtimestamp(stats.get("breaktime")).strftime("%Hh %Mm %Ss"))
        print(info)
    
    def saldo(self):
        '''
        Print salo todo/done and time account
        '''
        reqw = Utils.getRequiredWork(time.time())
        width = settings.get("border_width")-11
        c1w=int(width/10*2)
        c2w=int(width/10*4)
        c3w=int(width/10*4)
        info=""
        info+=Utils.pbn()
        info+=Utils.pb("Time saldo:")
        info+=Utils.pb(Utils.pfb("",settings.get("border_width")-5))
        info+=Utils.pbn()
        info+=Utils.pb(Utils.pf("Entity",c1w)+" | "+Utils.pf("Required ",c2w)+" | "+Utils.pf("Worked ",c3w))
        info+=Utils.pb("-"*(settings.get("border_width")-5))
        info+=Utils.pb(Utils.pf("Year",c1w)+" | "+Utils.pf(str(reqw.get("year")/3600)+"h",c2w)+" | "+Utils.pf("",c3w))
        info+=Utils.pb(Utils.pf("Month",c1w)+" | "+Utils.pf(str(reqw.get("month")/3600)+"h",c2w)+" | "+Utils.pf("",c3w))
        info+=Utils.pb(Utils.pf("Week",c1w)+" | "+Utils.pf(str(reqw.get("week")/3600)+"h",c2w)+" | "+Utils.pf("",c3w))
        info+=Utils.pb(Utils.pf("Today",c1w)+" | "+Utils.pf(str(reqw.get("day")/3600)+"h",c2w)+" | "+Utils.pf("",c3w))
        info+=Utils.pbn()
        print(info)
        
        
    
    def month(self):
        self.l.info("Generating month visualization...")
    
    def week(self):
        self.l.info("Generating week visualization...")
    
    def last(self):
        self.l.info("Generating visualization from last closed workday...")
    
    def open(self):
        self.l.info("Generating visualization from currently open workday...")
    