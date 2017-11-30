import time
import os
import json
import logging
from src import settings
from datetime import datetime
from json.decoder import JSONDecoder
from json.encoder import JSONEncoder
from _tracemalloc import start

class Workday():
    SUID="53d00e3e-75c4-4fae-866a-1f54b6a45fa7_r1"
    
    def __init__(self,
        start=time.time(),#Starts on creation
        breaks=[],#[{start:timestamp,end:timestamp}] we could ignore them
        end=None, #When persisted only 1 Workday must have != None:
        serialid=SUID): 
        self.l = logging.getLogger(__name__+"."+self.__class__.__name__)
        self.start=start
        self.breaks=breaks
        self.end=end
        self.serialid=Workday.SUID
        
    @staticmethod
    def _getPath(historydir, date):
        year=date.strftime("%Y")
        month=date.strftime("%m")
        day=date.strftime("%d")
        return os.path.join(historydir,year+"/"+month+"/"+day+".json")
    
    @staticmethod
    def loadLast(historydir):
        '''
        Returns the last not yet closed <Workday>
        '''
        now=time.time()
        for root,dirs,files in os.walk(historydir,topdown=True):
            for name in files:
                #open & deserialize
                with open(os.path.join(root,name),"r") as f:
                    wd = json.load(f,cls=WorkdayJSONDecoder)
                    if(not wd.end):
                        return {"date":datetime.fromtimestamp(wd.start).date(), "workday":wd,"timestamp":wd.start}
        return {"date":datetime.fromtimestamp(now).date(), "workday":None,"timestamp":now}
    
    @staticmethod
    def loadDay(historydir,ts):
        '''
        Returns the <Workday> within the given timestamp like
        {workday:<Workday>, date:<Date>}
        '''
        expPath=Workday._getPath(historydir,datetime.fromtimestamp(ts).date())
        wd=None
        if(os.path.isfile(expPath)):
            with open(expPath) as f:
                    wd = json.load(f,cls=WorkdayJSONDecoder)
        return {"date":datetime.fromtimestamp(ts).date(), "workday":wd,"timestamp":ts}
    
    @staticmethod
    def loadLastNDay(historydir,ts,offset=0):
        '''
        Returns the Nth closed <Workday> within the year of the given timestamp
        or None. Offset 0 would be the last closed <Workday> 1 the second last, etc.
        '''
        from src.utils import Utils
        wd=None
        searchOffset=0
        for ydObj in reversed(Utils.getYearDates(ts)):
            loadedWDObj=Workday.loadDay(historydir,ydObj.get("timestamp"))
            lwd=loadedWDObj.get("workday")
            if(lwd and lwd.end and searchOffset == offset):
                wd=lwd
                break
            elif(lwd and lwd.end):
                searchOffset+=1
        return wd
    
    @staticmethod
    def loadWeek(historydir,ts):
        '''
        Returns a <Workday> for each weekday within the week of the given timestamp like
        [
            {workday:<Workday>, date:<Date>}...
        ]
        '''
        from src.utils import Utils
        workdays=[]
        for weekdate in Utils.getWeekdates(ts):
            wd=None
            expPath=Workday._getPath(historydir,weekdate.get("date"))
            #open & deserialize
            if(os.path.isfile(expPath)):
                with open(expPath) as f:
                    wd = json.load(f,cls=WorkdayJSONDecoder)
            workdays.append({"date":weekdate.get("date"),"workday":wd,"timestamp":weekdate.get("timestamp")})
        return workdays
    
    @staticmethod
    def loadMonth(historydir,ts):
        '''
        Returns all collected workdays within the month of the given timestamp
        '''
        from src.utils import Utils
        workdays=[]
        for monthdate in Utils.getMonthdates(ts):
            wd=None
            expPath=Workday._getPath(historydir,monthdate.get("date"))
            #open & deserialize
            if(os.path.isfile(expPath)):
                with open(expPath) as f:
                    wd = json.load(f,cls=WorkdayJSONDecoder)
            workdays.append({"date":monthdate.get("date"),"workday":wd,"timestamp":monthdate.get("timestamp")})
        return workdays
        
    @staticmethod
    def loadYear(historydir,ts):
        '''
        Returns all collected workdays within the year of the given timestamp
        '''
        workdays=[]
        from src.utils import Utils
        for yeardate in Utils.getYearDates(ts):
            wd=None
            expPath=Workday._getPath(historydir,yeardate.get("date"))
            #open & deserialize
            if(os.path.isfile(expPath)):
                with open(expPath) as f:
                    wd = json.load(f,cls=WorkdayJSONDecoder)
            workdays.append({"date":yeardate.get("date"),"workday":wd,"timestamp":yeardate.get("timestamp")})
        return workdays
        
    def persist(self, historydir, askoverride=False):
        '''
        persists this workday object
        '''
        
        #(Re)Create history directory in case it got deleted
        if(not os.path.isdir(historydir)):
            os.makedirs(historydir, mode=0o750)

        #Ensure the destination path
        dstfile = self._getWDF(historydir)
        dstdir = os.path.dirname(dstfile)
        if(not os.path.isdir(dstdir)):
            os.makedirs(dstdir, mode=0o750)
        
        if(os.path.isfile(dstfile) and askoverride):
            self.l.error("The file for this workday already exists")
            uip = input("Override? [N/y] :")
            if(uip.lower() != "y"):
                exit(0)
                
        #Serialize as json
        with open(dstfile,"w") as f:
            json.dump(self,f,cls=WorkdayJSONEncoder,indent=4)
        
        self.l.info("Persisted "+dstfile)
            
    def _getWDF(self, historydir):
        '''
        returns the path for this Workday object
        '''
        dstyear=datetime.fromtimestamp(self.start).strftime("%Y")
        dstmonth=datetime.fromtimestamp(self.start).strftime("%m")
        dstday=datetime.fromtimestamp(self.start).strftime("%d")
        return os.path.join(historydir,dstyear+"/"+dstmonth+"/"+dstday+".json")

        
class WorkdayJSONDecoder(JSONDecoder):
    '''
    JSON decoder for Workday object
    '''
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self,object_hook=self.decodeWorkday, *args, **kwargs)
        
    def decodeWorkday(self,object):
        
        #to exclude breaks
        if("serialid" not in object or Workday.SUID not in object.values()):
            return object 
        
        #everything else belongs to the main object
        return Workday(
            start=object.get("start"),
            breaks=object.get("breaks"),
            end=object.get("end"),
        )
        
class WorkdayJSONEncoder(JSONEncoder):
    '''
    JSON encoder for Workday object
    '''
    def default(self,object):
        if(isinstance(object, Workday)):
            obj = {
                "start":object.start,
                "breaks":object.breaks,
                "end":object.end,
                "serialid":object.serialid
            }
            return obj
        else:
            #default encoder
            return JSONEncoder.default(self,object)