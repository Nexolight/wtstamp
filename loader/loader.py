import yaml
import os
import sys

class Loader():
    def __init__(self):
        pass
    
    @staticmethod
    def loadSettings():
        '''
        Loads modifies and returns the settings as dict
        '''
        home = os.path.expanduser("~")
        spath = os.path.dirname(sys.argv[0])
        preferedSettings=os.path.join(spath,"settings.yaml")
        templateSettings=os.path.join(spath,"settings.yaml.template")
        sfile=templateSettings
        if(os.path.isfile(preferedSettings)):
            sfile=preferedSettings
        settings = yaml.load(open(sfile,"r"))
        for k,v in settings.items():
            if(isinstance(v,str)):
                settings.update({k:v.replace("USERHOME", home)})
        settings.update({
            "i_home":home,
            "i_spath":spath
            })
        return settings