import logging
import os
import time
from datetime import datetime
from src import settings
from src.utils import Utils
from models.models import Workday
from math import ceil,floor

class Visualizer():
    def __init__(self):
        self.l = logging.getLogger(__name__+"."+self.__class__.__name__)
        self.historydir = settings.get("history_data")
        pass
    
    def day(self):
        '''
        Print infos about the ongoing workday
        '''
        #We want to know the last active workday
        lastwd = Workday.loadLast(settings.get("history_data"))
        info=Utils.head("Active workday")
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
            info+=Utils.pb("required       >> "+datetime.utcfromtimestamp(settings.get("minutes_per_day")*60).strftime("%Hh %Mm %Ss"))
            info+=Utils.pbn()
            info+=Utils.pb("worktime       >> "+datetime.utcfromtimestamp(stats.get("worktime")).strftime("%Hh %Mm %Ss"))
            info+=Utils.pb("breaktime      >> "+datetime.utcfromtimestamp(stats.get("breaktime")).strftime("%Hh %Mm %Ss"))
            info+=Utils.pbn()
            info+=Utils.pbdiv()
        print(info)
    
    def saldo(self):
        '''
        Print salo todo/done and time account
        '''
        reqw = Utils.getRequiredWork(time.time())
        donew = Utils.getDoneWork(self.historydir,time.time())
        lastwd = Workday.loadLast(settings.get("history_data"))
        width = settings.get("border_width")-11
        c1w=int(width/10*4)
        c2w=int(width/10*3)
        c3w=int(width/10*3)
        
        rhYear=str(floor(reqw.get("year")/3600))+"h "+str(floor(reqw.get("year")%3600/60))+"m"
        rhMonth=str(floor(reqw.get("month")/3600))+"h "+str(floor(reqw.get("month")%3600/60))+"m"
        rhWeek=str(floor(reqw.get("week")/3600))+"h "+str(floor(reqw.get("week")%3600/60))+"m"
        rhDay=str(floor(reqw.get("day")/3600))+"h "+str(floor(reqw.get("day")%3600/60))+"m"
        
        dhYear=str(floor(donew.get("year")/3600))+"h "+str(floor(donew.get("year")%3600/60))+"m"
        dhMonth=str(floor(donew.get("month")/3600))+"h "+str(floor(donew.get("month")%3600/60))+"m"
        dhWeek=str(floor(donew.get("week")/3600))+"h "+str(floor(donew.get("week")%3600/60))+"m"
        dhDay=str(floor(donew.get("day")/3600))+"h "+str(floor(donew.get("day")%3600/60))+"m"
        
        thAcc=Utils.formatDHM(-reqw.get("now")+donew.get("now"))
            
        info=info=Utils.head("Saldo")
        info+=Utils.pbn()
        info+=Utils.pb(Utils.pf("Entity",c1w)+" | "+Utils.pf("Required ",c2w)+" | "+Utils.pf("Worked ",c3w))
        info+=Utils.pb("-"*(settings.get("border_width")-5))
        info+=Utils.pb(Utils.pf("Year",c1w)+" | "+Utils.pf(rhYear,c2w)+" | "+Utils.pf(dhYear,c3w))
        info+=Utils.pb(Utils.pf("Month",c1w)+" | "+Utils.pf(rhMonth,c2w)+" | "+Utils.pf(dhMonth,c3w))
        info+=Utils.pb(Utils.pf("Week",c1w)+" | "+Utils.pf(rhWeek,c2w)+" | "+Utils.pf(dhWeek,c3w))
        if(lastwd and not lastwd.end and datetime.fromtimestamp(lastwd.start).date() != datetime.fromtimestamp(time.time()).date()):
            datestr=datetime.fromtimestamp(lastwd.start).date().strftime("Today (%d.%m - Now)")
            dhLDay=str(floor(donew.get("day")/3600))+"h "+str(floor(Utils.getWDStats(lastwd).get("worktime")%3600/60))+"m"
            info+=Utils.pb(Utils.pf(datestr,c1w)+" | "+Utils.pf(rhDay,c2w)+" | "+Utils.pf(dhLDay,c3w))
        else:
            info+=Utils.pb(Utils.pf("Today",c1w)+" | "+Utils.pf(rhDay,c2w)+" | "+Utils.pf(dhDay,c3w))
        info+=Utils.pb("-"*(settings.get("border_width")-5))
        info+=Utils.pbn()
        info+=Utils.pb("Time account: "+thAcc)
        info+=Utils.pbn()
        info+=Utils.pbdiv()
        print(info)
    
    def month(self, ts):
        '''
        Print a month table from the given month
        '''
        info=Utils.head("This month:")
        info+=Utils.pbn()
        info+=self._getTbl(Workday.loadMonth(self.historydir,ts))
        info+=Utils.pb(Utils.pfdl())
        info+=Utils.pbn()
        info+=Utils.pbdiv()
        print(info)
    
    def week(self, ts):
        info=Utils.head("This week:")
        info+=Utils.pbn()
        info+=self._getTbl(Workday.loadWeek(self.historydir,ts))
        info+=Utils.pb(Utils.pfdl())
        info+=Utils.pbn()
        info+=Utils.pbdiv()
        print(info)
    
    def _getTbl(self, loadedWDs):
        '''
        Returns a table view of the given loaded workdays
        '''
        info=""
        width = settings.get("border_width")-14
        c1=int(width/10*3)
        c2=int(width/10*3)
        c3=int(width/10*2)
        c4=int(width/10*2)
        info+=Utils.pb(Utils.pf("Day",c1)+" | "+Utils.pf("Range",c2)+" | "+Utils.pf("Required",c3)+" | "+Utils.pf("Worked",c4))
        reqdstr=Utils.formatHM(settings.get("minutes_per_day")*60)
        for wdIM in loadedWDs:
            t_wd=wdIM.get("workday")
            t_ts=wdIM.get("timestamp")
            t_dt=datetime.fromtimestamp(t_ts).strftime(settings.get("date_format"))
            if(t_wd):
                info+=Utils.pb(Utils.pfl())
                worktime=Utils.formatHM(Utils.getWDStats(t_wd).get("worktime"))
                w_wds=t_wd.start
                w_wde=t_wd.end
                if(not w_wde):#currently open day
                    w_wde=time.time()
                #range
                datestr=datetime.fromtimestamp(w_wds).strftime(settings.get("date_format"))
                wdStart=datetime.fromtimestamp(w_wds).strftime("%H:%M")
                wdEnd=datetime.fromtimestamp(w_wde).strftime("%H:%M")
                
                info+=Utils.pb(Utils.pf(datestr,c1)+" | "+Utils.pf(wdStart+" - "+wdEnd,c2)+" | "+Utils.pf(reqdstr,c3)+" | "+Utils.pf(worktime,c4))
            elif(Utils.isFree(t_ts)):
                pass
            else:
                info+=Utils.pb(Utils.pfl())
                info+=Utils.pb(Utils.pf(t_dt,c1)+" | "+Utils.pf(" ",c2)+" | "+Utils.pf(reqdstr,c3)+" | "+Utils.pf(Utils.formatHM(0),c4))
                #info+=Utils.pb(str(wkm.get("date"))+" free")
        return info
    
    
    def last(self):
        self.l.info("Generating visualization from last closed workday...")
    
    def open(self):
        self.l.info("Generating visualization from currently open workday...")
    
    
    
    