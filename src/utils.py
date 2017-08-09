from datetime import datetime
from src import settings
from calendar import monthrange
import time

class Utils:
    
    WEEKDAYS=["monday","tuesday","wednesday","thursday", "friday", "saturday", "sunday"]
    MONTHS=["january","february","march","april","may","june","july","august","september","november","december"]
    
    def __init__(self):
        pass
    
    @staticmethod
    def getRequiredWork(ts):
        '''
        Returns a dict with the work required for the current:
        {
            day:<utc_seconds>
            week:<utc_seconds>
            month:<utc_seconds>
            year:<utc_seconds>
        }
        '''
        
        daystr = datetime.fromtimestamp(ts).strftime("%A").lower()
        datestr = datetime.fromtimestamp(ts).strftime("%d.%m.%Y")
        day=Utils.getRequiredWorkDay(ts)
        week=Utils.getRequiredWorkWeek(ts)
        month=Utils.getRequiredWorkMonth(ts)
        year=Utils.getRequiredWorkYear(ts)
        return{
            "day":day,
            "week":week,
            "month":month,
            "year":year
        }
        
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
        daystr = datetime.fromtimestamp(ts).strftime("%A").lower()
        
        work=0
        weekdates=[]
        weekday_index = Utils.WEEKDAYS.index(daystr)
        weekstartts = ts - (weekday_index*86400)
        weekendts = ts + ((len(Utils.WEEKDAYS)-(weekday_index+1))*86400)
        weekend = datetime.fromtimestamp(weekendts).strftime("%d.%m.%Y")
        iterts=weekstartts
        while True:
            #add date to array
            iterdate=datetime.fromtimestamp(iterts).strftime("%d.%m.%Y")
            weekdates.append(iterdate)
            
            #break when the end of the week is reached
            if(iterdate==weekend):
                break
            
            #Add a day
            iterts+=86400
            
        for date in weekdates:#cumulate time for all non free days
            datets=datetime.strptime(date, "%d.%m.%Y").timestamp()
            if(not Utils.isFree(datets)):
                work+=settings.get("minutes_per_day")*60
        
        return work
        
    
    @staticmethod
    def getRequiredWorkMonth(ts):
        '''
        returns the work to be done this month
        '''
        work=0
        dateobj=datetime.fromtimestamp(ts).date()
        monthdays = monthrange(dateobj.year,dateobj.month)[1]#get the days of the month
        
        for day in range(1,monthdays+1):
            datets=datetime.strptime(str(day)+"."+str(dateobj.month)+"."+str(dateobj.year), "%d.%m.%Y").timestamp()
            if(not Utils.isFree(datets)):
                work+=settings.get("minutes_per_day")*60
        return work
    
    
    @staticmethod
    def getRequiredWorkYear(ts):
        dateobj=datetime.fromtimestamp(ts).date()
        work=0
        for month in range(1,13):
            mts = datetime.strptime(str(1)+"."+str(month)+"."+str(dateobj.year), "%d.%m.%Y").timestamp()
            work+=Utils.getRequiredWorkMonth(mts)
        return work
    
    @staticmethod
    def isFree(dt):
        '''
        Returns true when day of the date is either a holiday,
        specialday or non workday.
        '''
        daystr = datetime.fromtimestamp(dt).strftime("%A").lower()
        datestr = datetime.fromtimestamp(dt).strftime("%d.%m.%Y")
        yearstr = datetime.fromtimestamp(dt).strftime("%Y")
        
        #workdays from settings
        s_workdays=settings.get("workdays")
        
        #holidays from settings single or range - need to process
        s_holidays=[]
        for holiday in settings.get("holidays"):
            rng = holiday.split("-")
            if(len(rng)>1):
                startts=datetime.strptime(rng[0], "%d.%m.%Y").timestamp()#start of holidays
                endts=datetime.strptime(rng[1], "%d.%m.%Y").timestamp()#end of holidays
                enddate=datetime.fromtimestamp(endts).strftime("%d.%m.%Y")
                iterts=startts
                while True:
                    iterdate=datetime.fromtimestamp(iterts).strftime("%d.%m.%Y")
                    #Add day to array
                    s_holidays.append(iterdate)
                    
                    #break when we reach the final date
                    if(iterdate == enddate):
                        break
                    
                    #Add one day
                    iterts+=86400
                    
            else:
                s_holidays.append(holiday)
        
        #Special days in the settings miss the year
        s_specialdays=[]
        for specialday in settings.get("specialdays"):
            s_specialdays.append(specialday+"."+yearstr)
            
        if(daystr not in s_workdays or (datestr in s_holidays or datestr in s_specialdays)):
            return True
        return False
        
    
    @staticmethod
    def getDoneWork(wd):
        '''
        Returns a dict with the work done within the current:
        {
            day:<utc_seconds>
            week:<utc_seconds>
            month:<utc_seconds>
            year:<utc_seconds>
        }
        '''
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
    def pfb(text,size):
        '''
        Fills the given string with # up to the given count
        '''
        if(len(text)<size):
            return text+("#"*(size-len(text)))
        return text
        
        
        
        