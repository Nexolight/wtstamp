from datetime import datetime
from src import yamlsettings as settings
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
        day=Utils.getDoneWorkT("day",historydir,ts)
        week=Utils.getDoneWorkT("week",historydir,ts)
        month=Utils.getDoneWorkT("month",historydir,ts)
        year=Utils.getDoneWorkT("year",historydir,ts)
        now=year
            
        return {
            "now":now,
            "day":day,
            "week":week,
            "month":month,
            "year":year
        }
        
    @staticmethod
    def getDoneWorkT(type,historydir,ts):
        '''
        Returns the done work depending on <type> in seconds
        starting from year_swap as long as <ts> is above year_swap
        
        type can be:
        "year"
        "month"
        "week"
        "day"
        "until"
        '''
        work=0
        wdos=[]
        if(type=="year"):
            wdos=Workday.loadYear(historydir,ts)
        elif(type=="month"):
            wdos=Workday.loadMonth(historydir,ts)
        elif(type=="week"):
            wdos=Workday.loadWeek(historydir,ts)
        elif(type=="day"):
            wdd=Workday.loadDay(historydir,ts)
            if(not wdd.get("workday") and datetime.fromtimestamp(time.time()).date() == givenDate):
                wdos.append(Workday.loadLast(historydir)) #this happens when a workday is longer than 12pm
            else:
                wdos.append(wdd)
        elif(type=="until"):
            wdos=Workday.loadYear(historydir,ts)
        
        givenDate=datetime.fromtimestamp(ts).date()
        
        for wdo in wdos:
            if(not type=="until"):
                if(not wdo.get("workday") or not Utils.inCalc(wdo.get("workday").start)):
                    continue #Just a day without a saved workday object or out of our calc range
                work+=Utils.getWDStats(wdo.get("workday")).get("worktime")
            else:#type==until
                if(ts<wdos[0].get("timestamp")):# year_swap workaround
                    return work
                if(wdo.get("workday") and Utils.inCalc(wdo.get("workday").start)):
                    work+=Utils.getWDStats(wdo.get("workday")).get("worktime")
                if(type=="until" and wdo.get("date") == givenDate):
                    break # for "until" we break here
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
        now=Utils.getRequiredWorkT("until",time.time())
        day=Utils.getRequiredWorkT("day",ts)
        week=Utils.getRequiredWorkT("week",ts)
        month=Utils.getRequiredWorkT("month",ts)
        year=Utils.getRequiredWorkT("year",ts)
        return{
            "now":now,
            "day":day,
            "week":week,
            "month":month,
            "year":year
        }
        
        
        
    @staticmethod
    def getRequiredWorkT(type,ts):
        '''
        Returns the required work depending on <type> in seconds
        starting from year_swap as long as <ts> is above year_swap
        
        type can be:
        "year"
        "month"
        "week"
        "day"
        "until"
        '''
        work=0
        dates=[]
        if(type=="year"):
            dates=Utils.getYearDates(ts)
        elif(type=="month"):
            dates=Utils.getMonthdates(ts)
        elif(type=="week"):
            dates=Utils.getWeekdates(ts)
        elif(type=="day"):
            return Utils.getMinutesPerDay(ts)
        elif(type=="until"):
            dates=Utils.getYearDates(ts)
            
        if(ts<dates[0].get("timestamp")):# year_swap workaround
            return work
        
        givenDate=datetime.fromtimestamp(ts).date()
        for dat in dates:
            if(not Utils.isFree(dat.get("timestamp"))):
                work+=Utils.getMinutesPerDay(dat.get("timestamp"))
            
            #We want to stop here for "until" otherwise we
            #take all values.
            if(type=="until" and dat.get("date")==givenDate):
                break
        return work
    
    @staticmethod
    def getPreviousLastMonthDay(ts):
        '''
        Returns the last day of the previous month as a timestamp
        '''
        dat=datetime.fromtimestamp(ts).date()
        lYear=dat.year
        lMonth=dat.month-1
        if(lMonth<1):
            lMonth=12
            lYear-=1
        lDay=monthrange(lYear,lMonth)[1]
        return datetime.strptime(str(lDay)+"."+str(lMonth)+"."+str(lYear),"%d.%m.%Y").timestamp()
    
    @staticmethod
    def getPreviousLastYearDay(ts):
        '''
        Returns the last day of the previous "year" as a timestamp
        The start of the year is defined by year_swap, so this is one day
        before year_swap
        '''
        datnow=datetime.fromtimestamp(ts).date()
        swap=settings.get("year_swap").split(".")
        yearstart=datetime.strptime(swap[0]+"."+swap[1]+"."+str(datnow.year), "%d.%m.%Y").timestamp()
        return yearstart-86400
    
    @staticmethod
    def getPreviousLastWeekDay(ts):
        '''
        Returns the last day of the previous week as a timestamp
        '''
        while True:
            ts-=3600
            dat=datetime.fromtimestamp(ts).date()
            if(dat.weekday()==6):#sunday
                #strip time
                return datetime.strptime(str(dat.day)+"."+str(dat.month)+"."+str(dat.year), "%d.%m.%Y").timestamp()
        
    
    @staticmethod
    def inCalc(ts):
        '''
        Returns true when the day of the date is in the calc cycle.
        '''
        dat=datetime.fromtimestamp(ts).date()
        if settings.get("calc_cycles").get(dat):
            return True
    
    @staticmethod
    def getMinutesPerDay(ts):
        '''
        Returns the required worktime in minutes for the date at the given timestamp
        '''
        return settings.get("calc_cycles").get(datetime.fromtimestamp(ts).date()).get("minutes_per_day")*60
    
    @staticmethod
    def isFree(dt):
        '''
        Returns true when the day of the date is either a holiday,
        specialday, non workday or not within the calc cycle.
        '''
        dat = datetime.fromtimestamp(dt).date()
        daystr = datetime.fromtimestamp(dt).strftime("%A").lower()
        datestr = datetime.fromtimestamp(dt).strftime("%d.%m.%Y")
        yearstr = datetime.fromtimestamp(dt).strftime("%Y")
        
        #holidays from settings
        s_holidays=settings.get("holidays")
        
        #Specialdays are free
        s_specialdays=[]
        for specialday in settings.get("specialdays"):
            s_specialdays.append(specialday+"."+yearstr)#Special days in the settings miss the year
        
        #Everything what is not in the calc_cycle is a free day
        if(not settings.get("calc_cycles").get(dat)):#only dates from a user defined range are there
            return True
        
        if(daystr not in settings.get("calc_cycles").get(dat).get("workdays") or (datestr in s_holidays or datestr in s_specialdays)):
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
                breaktime+=time.time()-breaks.get("start")
                last_stamp=breaks.get("start")
        worktime=last_stamp-wd.start
        worktime-=breaktime
        return {
            "worktime":worktime,
            "breaktime":breaktime
        }
    
    @staticmethod
    def evalEditDay(historydir, ts=None, noOpenDays=False):
        '''
        When no timestamp is given, 1st. the last open day is looked up, then
        2nd. the last closed day is looked up.
        if noOpenDays is True it will ignore not yet closed days
        In case a timestamp is given the specified day is looked up.
        returns <Workday> or None
        '''
        wd = None
        if(not ts):
            wdObj = Workday.loadLast(historydir)
            if(noOpenDays == True or not wdObj.get("workday")):
                wd = Workday.loadLastNDay(historydir,time.time());
            else:
                wd = wdObj.get("workday")
        else:
            wd = Workday.loadDay(historydir, ts).get("workday")
        return wd
        
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
    def pfb(text="",size=settings.get("border_width")-5,symbol="#"):
        '''
        Fills the given string with # up to the given count
        '''
        if(len(text)<size):
            return text+(symbol*(size-len(text)))
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
    def head(text, underline=settings.get("border_width")-5,symbol="#"):
        '''
        Returns a head
        '''
        str=""
        str+=Utils.pbn()
        str+=Utils.pb(text)
        str+=Utils.pb(Utils.pfb("",size=underline,symbol=symbol))
        return str
    
    @staticmethod
    def formatDecH(ts):
        return str(round(ts/3600,2))+"h"
    
    @staticmethod
    def formatDHM(ts,posSign=False):
        '''
        Formats seconds to a day, hours and minutes string
        '''
        txt=""
        if(ts<0):
          txt+="-"
          ts=abs(ts)  
        elif(posSign and ts>=0):
            txt+="+"
        wd=86400
        daysf=ts/wd
        if(daysf > 0):
            days=floor(daysf)
        else:
            days=ceil(daysf)
        txt+=str(days)+"d "
        ts=ts-(days*wd)
        hoursf=ts/3600
        if(hoursf > 0):
            hours=floor(hoursf)
        else:
            hours=ceil(hoursf)
        txt+=str(hours)+"h "
        minutesf=ts%3600/60
        if(minutesf > 0):
            minutes=floor(minutesf)
        else:
            minutes=ceil(minutesf)
        txt+=str(minutes)+"m "
        return txt
    
    @staticmethod
    def formatHM(ts,posSign=False):
        '''
        Formats seconds to a hours and minutes string
        '''
        txt=""
        if(ts<0):
          txt+="-"
          ts=abs(ts)  
        elif(posSign and ts>=0):
            txt+="+"
        hoursf=ts/3600
        if(hoursf > 0):
            hours=floor(hoursf)
        else:
            hours=ceil(hoursf)
        txt+=str(hours)+"h "
        minutesf=ts%3600/60
        if(minutesf > 0):
            minutes=floor(minutesf)
        else:
            minutes=ceil(minutesf)
        txt+=str(minutes)+"m "
        return txt
    
    @staticmethod
    def convertHMToSeconds(str, separator=":"):
        if(not str.count(separator) == 1):
            raise ValueError("Invalid format")
        arr = str.split(separator)
        s = 0
        s+=int(arr[0])*3600
        s+=int(arr[1])*60
        return s
        
        
        