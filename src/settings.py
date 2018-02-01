from datetime import datetime
from src import yamlsettings as settings
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
        
        tarrClc={}
        for cycle in settings.get("calc_cycles"):
            for workrange in cycle.get("range"):
                range = workrange.split("-")
                sDate=datetime.strptime(range[0], "%d.%m.%Y").date()
                eDate=datetime.strptime(range[1], "%d.%m.%Y").date()
                for dto in Utils.getDatesFromRange(sDate,eDate):
                    dayname=datetime.fromtimestamp(dto.get("timestamp")).strftime("%A").lower()
                    tarrClc.update({
                        datetime.fromtimestamp(dto.get("timestamp")).date():{
                            "minutes_per_day":cycle.get("minutes_per_day"),
                            "day":dayname,
                            "workdays":cycle.get("workdays")
                        }
                    })
        settings.update({"calc_cycles":tarrClc})
        
                