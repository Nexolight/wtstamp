import time
import os
import json
import logging
from datetime import datetime
from json.decoder import JSONDecoder
from json.encoder import JSONEncoder
from _tracemalloc import start

class Workday():
    def __init__(self,
        start=time.time(),#Starts on creation
        breaks=[],#[{start:timestamp,end:timestamp}] we could ignore them
        end=None,#When persisted only 1 Workday must have != None
        worktime=0):
        self.l = logging.getLogger(__name__+"."+self.__class__.__name__)
        self.start=start
        self.breaks=breaks
        self.end=end
        self.worktime=worktime
    
    @staticmethod
    def loadLast(historydir):
        for root,dirs,files in os.walk(historydir,topdown=True):
            for name in files:
                with open(os.path.join(root,name),"r") as f:
                    wd = json.load(f,cls=WorkdayJSONDecoder)
                    if(not wd.end):
                        return wd
        return None
        
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
            json.dump(self,f,cls=WorkdayJSONEncoder)
        
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
        if("worktime" not in object):
            return object 
        
        #everything else belongs to the main object
        return Workday(
            start=object.get("start"),
            breaks=object.get("breaks"),
            end=object.get("end"),
            worktime=object.get("worktime")
        )
        
class WorkdayJSONEncoder(JSONEncoder):
    '''
    JJSON encoder for Workday object
    '''
    def default(self,object):
        if(isinstance(object, Workday)):
            obj = {
                "start":object.start,
                "breaks":object.breaks,
                "end":object.end,
                "worktime":object.worktime
            }
            return obj
        else:
            #default encoder
            return JSONEncoder.default(self,object)