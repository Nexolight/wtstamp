import logging
import os
import time
from datetime import datetime
from src import yamlsettings as settings
from src.utils import Utils
from models.models import Workday
from math import ceil,floor

class Visualizer():
    def __init__(self):
        self.l = logging.getLogger(__name__+"."+self.__class__.__name__)
        self.historydir = settings.get("history_data")
        pass
    
    def test(self):
        pass
    
    def ongoing(self):
        '''
        Print infos about a workday
        '''
        #We want to know the last active workday
        lastwd = Workday.loadLast(settings.get("history_data")).get("workday")
        if(lastwd):
            daystr=datetime.fromtimestamp(lastwd.start).strftime(settings.get("date_format"))
            info=Utils.head("Active Workday: "+daystr,symbol="~")
            info+=Utils.pbn()
            info+=self._getSingleDay(lastwd)
            info+=Utils.pbn()
            info+=Utils.pbdiv()
            print(info)
            return
        self.l.error("Could not find the last open workday")
        
    def last(self):
        '''
        Prints the last closed day
        '''
        #dateObjNow=datetime.fromtimestamp(time.time()).date()
        wd=Workday.loadLastNDay(self.historydir,time.time())
        if(wd):
            daystr=datetime.fromtimestamp(wd.start).strftime(settings.get("date_format"))
            info=Utils.head("Day: "+daystr,symbol="~")
            info+=Utils.pbn()
            info+=self._getSingleDay(wd)
            info+=Utils.pbn()
            info+=Utils.pbdiv()
            print(info)
            return
        self.l.error("Could not find the last closed workday")
        
    def day(self,ts):
        '''
        Prints the given day
        '''
        wdo=Workday.loadDay(self.historydir,ts)
        wd=wdo.get("workday")
        if(wd):
            daystr=datetime.fromtimestamp(wd.start).strftime(settings.get("date_format"))
            info=Utils.head("Day: "+daystr,symbol="~")
            info+=Utils.pbn()
            info+=self._getSingleDay(wd)
            info+=Utils.pbn()
            info+=Utils.pbdiv()
            print(info)
            return
        self.l.error("Could not find the specified day: "+datetime.fromtimestamp(ts).strftime(settings.get("date_format")))
    
    def saldo(self):
        '''
        Print salo todo/done and time account
        '''
        now=time.time()
        nowd=datetime.fromtimestamp(now)
        reqw = Utils.getRequiredWork(now)
        donew = Utils.getDoneWork(self.historydir,now)
        lastwd = Workday.loadLast(settings.get("history_data")).get("workday")
        width = settings.get("border_width")-11
        c1w=int(width/10*4)
        c2w=int(width/10*3)
        c3w=int(width/10*3)
        
        rhYear=Utils.formatHM(reqw.get("year"))
        rhMonth=Utils.formatHM(reqw.get("month"))
        rhWeek=Utils.formatHM(reqw.get("week"))
        rhDay=Utils.formatHM(reqw.get("day"))

        
        dhYear=Utils.formatHM(donew.get("year"))
        dhMonth=Utils.formatHM(donew.get("month"))
        dhWeek=Utils.formatHM(donew.get("week"))
        dhDay=Utils.formatHM(donew.get("day"))
        
        thAcc=Utils.formatHM(-reqw.get("now")+donew.get("now"))
        switchDate=settings.get("year_swap")
            
        info=info=Utils.head("Saldo")
        info+=Utils.pbn()
        info+=Utils.pb(Utils.pf("Entity",c1w)+" | "+Utils.pf("Required ",c2w)+" | "+Utils.pf("Worked ",c3w))
        info+=Utils.pb("-"*(settings.get("border_width")-5))
        info+=Utils.pb(Utils.pf("Year (until "+switchDate+")",c1w)+" | "+Utils.pf(rhYear,c2w)+" | "+Utils.pf(dhYear,c3w))
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
        info+=Utils.pb("Time account (right now): "+thAcc)
        info+=Utils.pbn()
        info+=Utils.pbdiv()
        print(info)
        
    def year(self, ts):
        '''
        Print a month table from the given month
        '''
        info=Utils.head("Year view:")
        info+=Utils.pbn()
        info+=self._getTbl(Workday.loadYear(self.historydir,ts),saldoBefore=0)
        info+=Utils.pbn()
        info+=Utils.pbdiv()
        print(info)
    
    def month(self, ts):
        '''
        Print a month table from the given month
        '''
        info=Utils.head("Month view:")
        info+=Utils.pbn()
        #print(Utils.getDoneWorkT("until",self.historydir,Utils.getPreviousLastMonthDay(ts)))
        #print(Utils.getRequiredWorkT("until",Utils.getPreviousLastMonthDay(ts)))
        #print(Utils.getPreviousLastMonthDay(ts))
        saldoBefore=Utils.getDoneWorkT("until",self.historydir,Utils.getPreviousLastMonthDay(ts))-Utils.getRequiredWorkT("until",Utils.getPreviousLastMonthDay(ts))
        info+=self._getTbl(Workday.loadMonth(self.historydir,ts),saldoBefore)
        info+=Utils.pbn()
        info+=Utils.pbdiv()
        print(info)
    
    def week(self, ts):
        info=Utils.head("Week view:")
        info+=Utils.pbn()
        saldoBefore=Utils.getDoneWorkT("until",self.historydir,Utils.getPreviousLastWeekDay(ts))-Utils.getRequiredWorkT("until",Utils.getPreviousLastWeekDay(ts))
        info+=self._getTbl(Workday.loadWeek(self.historydir,ts),saldoBefore)
        info+=Utils.pbn()
        info+=Utils.pbdiv()
        print(info)
    
    def _getTbl(self, loadedWDs, saldoBefore=0):
        '''
        Returns a table view of the given loaded workdays
        '''
        info=""
        width = settings.get("border_width")-14
        c1=int(width/10*2.5)
        c2=int(width/10*2)
        c3=int(width/10*1.25)
        c4=int(width/10*1.25)
        c5=int(width/10*3)
        sbstr=Utils.pf("Saldo",10)+" ("+Utils.formatHM(saldoBefore,posSign=True)+")"
        info+=Utils.pb(Utils.pf("Day",c1)+" | "+Utils.pf("Range",c2)+" | "+Utils.pf("Required",c3)+" | "+Utils.pf("Worked",c4)+" | "+Utils.pf(sbstr,c5))
        ssSaldo=saldoBefore
        for wdIM in loadedWDs:
            t_wd=wdIM.get("workday")
            t_ts=wdIM.get("timestamp")
            t_date=wdIM.get("date")
            t_dt=datetime.fromtimestamp(t_ts).strftime(settings.get("date_format"))
            if(t_date == datetime.fromtimestamp(time.time()).date()):
                t_dt=">> "+t_dt
            if(t_wd and not Utils.isFree(t_ts)):
                reqd=settings.get("calc_cycles").get(wdIM.get("date")).get("minutes_per_day")*60
                reqdstr=Utils.formatHM(reqd)
                info+=Utils.pb(Utils.pfl())
                wdstats=Utils.getWDStats(t_wd)
                worktime=Utils.formatHM(wdstats.get("worktime"))
                reqDiff=wdstats.get("worktime")-reqd
                ssSaldo+=reqDiff
                fSaldoStr=Utils.pf(Utils.formatHM(ssSaldo),10)+" ("+Utils.formatHM(reqDiff,posSign=True)+")"
                w_wds=t_wd.start
                w_wde=t_wd.end
                if(not w_wde):#currently open day
                    w_wde=time.time()
                wdStart=datetime.fromtimestamp(w_wds).strftime("%H:%M")
                wdEnd=datetime.fromtimestamp(w_wde).strftime("%H:%M")
                info+=Utils.pb(Utils.pf(t_dt,c1)+" | "+Utils.pf(wdStart+" - "+wdEnd,c2)+" | "+Utils.pf(reqdstr,c3)+" | "+Utils.pf(worktime,c4)+" | "+Utils.pf(fSaldoStr,c5))
            elif(Utils.isFree(t_ts)):#No need to print free days
                pass
            else:
                reqd=settings.get("calc_cycles").get(wdIM.get("date")).get("minutes_per_day")*60
                reqdstr=Utils.formatHM(reqd)
                
                fSaldoStr=""
                worktimeStr=""
                if(time.time() > t_ts):
                    ssSaldo-=reqd
                    fSaldoStr=Utils.pf(Utils.formatHM(ssSaldo),10)+" ("+Utils.formatHM(-reqd,posSign=True)+")"
                
                info+=Utils.pb(Utils.pfl())
                info+=Utils.pb(Utils.pf(t_dt,c1)+" | "+Utils.pf(" ",c2)+" | "+Utils.pf(reqdstr,c3)+" | "+Utils.pf("",c4)+" | "+Utils.pf(fSaldoStr,c5))
                #info+=Utils.pb(str(wkm.get("date"))+" free")
        info+=Utils.pb(Utils.pfb(symbol="~"))
        info+=Utils.pb(Utils.pf("End saldo:",c1)+Utils.pf("",c2+c3+c4+9)+" | "+Utils.pf(Utils.formatHM(ssSaldo),c5))
        info+=Utils.pb(Utils.pfb(symbol="="))
        return info
    
    def _getSingleDay(self, wd):
        '''
        Returns a complete view of the given workday
        '''
        width = settings.get("border_width")-8
        c1 = floor(width/10*3)
        c2 = floor(width/10*7)
        
        startStr=datetime.fromtimestamp(wd.start).strftime(settings.get("time_format"))
        endStr=datetime.fromtimestamp(time.time()).strftime(settings.get("time_format")+" (ongoing)")
        if(wd.end):
           endStr=datetime.fromtimestamp(wd.end).strftime(settings.get("time_format"))
        
        wdstats=Utils.getWDStats(wd)
        
        info=""
        if(Utils.isFree(wd.start)):
                info+=Utils.pb("THIS IS A FREE DAY")
                info+=Utils.pbn()
        info+=Utils.pb(Utils.pf("Day started",c1)+" > "+Utils.pf(startStr,c2))
        info+=Utils.pb(Utils.pf("Day ended",c1)+" > "+Utils.pf(endStr,c2))
        info+=Utils.pbn()
        if(len(wd.breaks) > 0):
            info+=Utils.pb(Utils.pf("breaks",c1)+" > "+Utils.pf(Utils.formatHM(wdstats.get("breaktime")),c2))
            for bk in wd.breaks:
                bkStart=bk.get("start")
                bkEnd=bk.get("end")
                bkStartStr=datetime.fromtimestamp(bkStart).strftime("%H:%M")
                bkEndStr=datetime.fromtimestamp(time.time()).strftime("%H:%M (ongoing)")
                if(bkEnd):
                    bkEndStr=datetime.fromtimestamp(bkEnd).strftime("%H:%M")
                info+=Utils.pb(Utils.pf("",c1)+" ^ "+Utils.pf(bkStartStr+" - "+bkEndStr,c2))
        else:
            info+=Utils.pb(Utils.pf("Breaks",c1)+" > "+Utils.pf("No breaks",c2))
        info+=Utils.pbn()
        info+=Utils.pb(Utils.pf("Worktime",c1)+" > "+Utils.pf(Utils.formatHM(wdstats.get("worktime")),c2))
        return info
                
    
    