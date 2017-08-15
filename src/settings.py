from datetime import datetime
from src import settings
from src.utils import Utils

class SettingsHelper:
    def __init__(self):
        pass
    
    @staticmethod
    def rangesToArray():
        '''
        updates the settings by converting all range type like dates into an array
        of dates
        '''
        
        #Holidays
        arrHolidays=[]
        for holiday in settings.get("holidays"):
            rng = holiday.split("-")
            if(len(rng)>1):
                sDate=datetime.strptime(rng[0], "%d.%m.%Y").date()
                eDate=datetime.strptime(rng[1], "%d.%m.%Y").date()
                dates=Utils.getDatesFromRange(sDate,eDate)
                for rngDate in dates:
                    dt=datetime.fromtimestamp(rngDate.get("timestamp")).strftime("%d.%m.%Y")
                    arrHolidays.append(dt)
            else:
                arrHolidays.append(holiday)
        settings.update({"holidays":arrHolidays})
        
        #Calc Cycles
        arrClc=[]
        for clc in settings.get("calc_cycles"):
            rng = clc.split("-")
            if(len(rng)>1):
                sDate=datetime.strptime(rng[0], "%d.%m.%Y").date()
                eDate=datetime.strptime(rng[1], "%d.%m.%Y").date()
                dates=Utils.getDatesFromRange(sDate,eDate)
                for rngDate in dates:
                    dt=datetime.fromtimestamp(rngDate.get("timestamp")).strftime("%d.%m.%Y")
                    arrClc.append(dt)
        settings.update({"calc_cycles":arrClc})