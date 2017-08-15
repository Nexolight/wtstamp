from datetime import datetime
from src import settings
from models.models import Workday
from calendar import monthrange
import time
from math import ceil,floor

class Utils:
    
    WEEKDAYS=["monday","tuesday","wednesday","thursday", "friday", "saturday", "sunday"]
    MONTHS=["january","february","march","april","may","june","july","august","september","november","december"]
    
    def __init__(self):
        pass
    
    @staticmethod
    def test():
        Utils.getRequiredWorkYear(time.time())
    
    @staticmethod
    def getDatesFromRange(dS,dE):
        '''
        Returns an array with all dates within the given range
        (includes start & end)
        like:
        [
            {"date": <Date>, "timestamp":<utc_seconds>}...
        ]
        '''
        iterts = datetime.strptime(str(dS.day)+"."+str(dS.month)+"."+str(dS.year), "%d.%m.%Y").timestamp()
        iterdate=datetime.fromtimestamp(iterts).date()
        dates=[{"date":iterdate,"timestamp":iterts}]
        while True:
            iterts=iterts+86400
            iterdate=datetime.fromtimestamp(iterts).date()
            dates.append({"date":iterdate, "timestamp":iterts})
            if(iterdate == dE):
                break
        return dates
    
    @staticmethod
    def getWeekdates(ts):
        '''
        Returns an array with all dates within the week of the given timestamp
        like:
        [
            {"date": <Date>, "timestamp":<utc_seconds>}...
        ]
        '''
        daystr = datetime.fromtimestamp(ts).strftime("%A").lower()
        weekdates=[]
        weekday_index = Utils.WEEKDAYS.index(daystr)
        weekstartts = ts - (weekday_index*86400)
        weekendts = ts + ((len(Utils.WEEKDAYS)-(weekday_index+1))*86400)
        weekend = datetime.fromtimestamp(weekendts).strftime("%d.%m.%Y")
        iterts=weekstartts
        
        while True:
            #add date to array
            iterdate=datetime.fromtimestamp(iterts).strftime("%d.%m.%Y")
            weekdates.append({"date":datetime.fromtimestamp(iterts).date(),"timestamp":iterts})
            
            #break when the end of the week is reached
            if(iterdate==weekend):
                break
            
            #Add a day
            iterts+=86400
            
        return weekdates
    
    @staticmethod
    def getMonthdates(ts):
        '''
        Returns an array with all dates within the month of the given timestamp
        like:
        [
            {"date": <Date>, "timestamp":<utc_seconds>}...
        ]
        '''
        monthdates=[]
        dateobj=datetime.fromtimestamp(ts).date()
        monthdays = monthrange(dateobj.year,dateobj.month)[1]#get the days of the month
        for day in range(1,monthdays+1):
            datets=datetime.strptime(str(day)+"."+str(dateobj.month)+"."+str(dateobj.year), "%d.%m.%Y").timestamp()
            monthdates.append({"date":datetime.fromtimestamp(datets).date(),"timestamp":datets})
        return monthdates
    
    @staticmethod
    def getYearDates(ts):
        '''
        Returns an array with all dates within the year of the given timestamp
        based on the year_swap setting
        like:
        [
            {"date": <Date>, "timestamp":<utc_seconds>}...
        ]
        '''
        yeardates=[]
        dateobj=datetime.fromtimestamp(ts).date()
        dStart=datetime.strptime(settings.get("year_swap")+"."+str(dateobj.year),"%d.%m.%Y").date()
        lDayTs=datetime.strptime(settings.get("year_swap")+"."+str(dateobj.year),"%d.%m.%Y").timestamp()-86400
        lDayDt=datetime.fromtimestamp(lDayTs).date()
        dEnd=datetime.strptime(str(lDayDt.day)+"."+str(lDayDt.month)+"."+str(dateobj.year+1),"%d.%m.%Y").date()
        return Utils.getDatesFromRange(dStart,dEnd)
    
    @staticmethod
    def getDoneWork(historydir, ts):
        '''
        Returns a dict with the work done in the current:
        {
            "now":<utc_seconds>
            "day":<utc_seconds>
            "week":<utc_seconds>
            "month":<utc_seconds>
            "year":<utc_seconds>
        }
        '''
        day=Utils.getDoneWorkDay(historydir,ts)
        week=Utils.getDoneWorkWeek(historydir,ts)
        month=Utils.getDoneWorkMonth(historydir,ts)
        year=Utils.getDoneWorkYear(historydir,ts)
        now=year
            
        return {
            "now":now,
            "day":day,
            "week":week,
            "month":month,
            "year":year
        }
    
    @staticmethod
    def getDoneWorkDay(historydir,ts):
        '''
        Returns the work done at the given day in seconds
        '''
        dateobj=datetime.fromtimestamp(ts).date()
        wdd = Workday.loadDay(historydir,ts)
        #Try to use the not yet closed day if any when no file for the current day exists
        if(not wdd.get("workday") and datetime.fromtimestamp(time.time()).date() == datetime.fromtimestamp(ts).date()):
            lwd=Workday.loadLast(historydir)
            if(lwd and Utils.inCalc(lwd.start)):
                return Utils.getWDStats().get("worktime")
        elif(wdd.get("workday") and Utils.inCalc(wdd.get("workday").start)):
            return Utils.getWDStats(wdd.get("workday")).get("worktime")
        return 0
    
    @staticmethod
    def getDoneWorkWeek(historydir,ts):
        '''
        Returns the work done within the week of the given timestamp in seconds
        '''
        work=0
        for wdw in Workday.loadWeek(historydir,ts):
            if(wdw.get("workday") and Utils.inCalc(wdw.get("workday").start)):
                work+=Utils.getWDStats(wdw.get("workday")).get("worktime")
        return work
    
    @staticmethod
    def getDoneWorkMonth(historydir,ts):
        '''
        Returns the work done within the month of the given timestamp in seconds
        '''
        work=0
        for wdm in Workday.loadMonth(historydir,ts):
            if(wdm.get("workday") and Utils.inCalc(wdm.get("workday").start)):
                work+=Utils.getWDStats(wdm.get("workday")).get("worktime")
        return work
    
    @staticmethod
    def getDoneWorkYear(historydir,ts):
        '''
        Returns the work done within the year of the given timestamp in seconds
        '''
        work=0
        for wdy in Workday.loadYear(historydir,ts):
            if(wdy.get("workday") and Utils.inCalc(wdy.get("workday").start)):
                work+=Utils.getWDStats(wdy.get("workday")).get("worktime")
        return work
            
    
    @staticmethod
    def getRequiredWork(ts):
        '''
        Returns a dict with the work required for the current:
        {
            "now":<utc_seconds>
            "day":<utc_seconds>
            "week":<utc_seconds>
            "month":<utc_seconds>
            "year":<utc_seconds>
        }
        '''
        now=Utils.getRequiredWorkNow()
        day=Utils.getRequiredWorkDay(ts)
        week=Utils.getRequiredWorkWeek(ts)
        month=Utils.getRequiredWorkMonth(ts)
        year=Utils.getRequiredWorkYear(ts)
        return{
            "now":now,
            "day":day,
            "week":week,
            "month":month,
            "year":year
        }
        
    @staticmethod
    def getRequiredWorkNow():
        work=0
        now=time.time()
        for mothdts in Utils.getYearDates(now):
            if(not Utils.isFree(mothdts.get("timestamp"))):
                work+=settings.get("minutes_per_day")*60
            if(mothdts.get("date")==datetime.fromtimestamp(now).date()):
                break
        return work;
        
    @staticmethod
    def getRequiredWorkDay(ts):
        '''
        returns the work to be done this day
        '''
        if(not Utils.isFree(ts)):
            return settings.get("minutes_per_day")*60
        return 0
    
    @staticmethod
    def getRequiredWorkWeek(ts):
        '''
        returns the work to be done this week
        '''
        work=0
        for weekdate in Utils.getWeekdates(ts): #cumulate time for all non free days
            if(not Utils.isFree(weekdate.get("timestamp"))):
                work+=settings.get("minutes_per_day")*60
        return work
        
    
    @staticmethod
    def getRequiredWorkMonth(ts):
        '''
        returns the work to be done this month
        '''
        work=0
        for wkd in Utils.getMonthdates(ts):
            if(not Utils.isFree(wkd.get("timestamp"))):
                work+=settings.get("minutes_per_day")*60
        return work
    
    
    @staticmethod
    def getRequiredWorkYear(ts):
        work=0
        for mothdts in Utils.getYearDates(ts):
            if(not Utils.isFree(mothdts.get("timestamp"))):
                work+=settings.get("minutes_per_day")*60
        return work
    
    @staticmethod
    def inCalc(ts):
        '''
        Returns true when the day of the date is in the calc cycle.
        '''
        strdate=datetime.fromtimestamp(ts).strftime("%d.%m.%Y")
        if strdate in settings.get("calc_cycles"):
            return True
    
    @staticmethod
    def isFree(dt):
        '''
        Returns true when the day of the date is either a holiday,
        specialday, non workday or not within the calc cycle.
        '''
        daystr = datetime.fromtimestamp(dt).strftime("%A").lower()
        datestr = datetime.fromtimestamp(dt).strftime("%d.%m.%Y")
        yearstr = datetime.fromtimestamp(dt).strftime("%Y")
        
        #workdays from settings
        s_workdays=settings.get("workdays")
        
        #holidays from settings
        s_holidays=settings.get("holidays")
        
        #Special days in the settings miss the year
        s_specialdays=[]
        for specialday in settings.get("specialdays"):
            s_specialdays.append(specialday+"."+yearstr)
            
        if(datestr not in settings.get("calc_cycles")):
            return True
        
        if(daystr not in s_workdays or (datestr in s_holidays or datestr in s_specialdays)):
            return True
        return False
    
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
                out+=rawstring[0:end]+fill+"| \n"
                rawstring=rawstring[end:len(rawstring)+1]
        return out
    
    @staticmethod
    def pbn():
        '''
        Returns a newline with decorated border
        '''
        return "|"+(" "*(settings.get("border_width")-3))+"|\n"
    
    @staticmethod
    def pbdiv():
        '''
        Returns a dividing line
        '''
        return "|"+("-"*(settings.get("border_width")-3))+"|\n"
    
    @staticmethod
    def pf(text,size):
        '''
        Fills the given string with spaces up to the given count
        '''
        if(len(text)<size):
            return text+(" "*(size-len(text)))
        return text
    
    @staticmethod
    def pfb(text="",size=settings.get("border_width")-5):
        '''
        Fills the given string with # up to the given count
        '''
        if(len(text)<size):
            return text+("#"*(size-len(text)))
        return text
    
    @staticmethod
    def pfdl(text="",size=settings.get("border_width")-5):
        '''
        Fills the given string with = up to the given count
        '''
        if(len(text)<size):
            return text+("="*(size-len(text)))
        return text
    
    @staticmethod
    def pfl(text="",size=settings.get("border_width")-5):
        '''
        Fills the given string with - up to the given count
        '''
        if(len(text)<size):
            return text+("-"*(size-len(text)))
        return text
    
    @staticmethod
    def head(text):
        '''
        Returns a head
        '''
        str=""
        str+=Utils.pbn()
        str+=Utils.pb(text)
        str+=Utils.pb(Utils.pfb(""))
        return str
    
    @staticmethod
    def formatDHM(ts):
        txt=""
        wd=settings.get("minutes_per_day")*60
        days=floor(ts/wd)
        txt+=str(days)+"wd "
        ts=ts-(days*wd)
        txt+=str(floor(ts/3600))+"h "
        txt+=str(floor(ts%3600/60))+"m "
        return txt
    
    @staticmethod
    def formatHM(ts):
        txt=""
        txt+=str(floor(ts/3600))+"h "
        txt+=str(floor(ts%3600/60))+"m "
        return txt
        
        
        