import os
from loader.loader import Loader
yamlsettings = Loader.loadSettings()

try:
    os.makedirs(yamlsettings.get("application_data"), mode=0o750, exist_ok=True)
    yamlsettings.update({"history_data":os.path.join(yamlsettings.get("application_data"),"history")})
except OSError:
    print("Not enough access to create: "+yamlsettings.get("application_data"))
    exit(1)
import logging.config
from sharedsrc.logger import WTSTAMP_LOG, CON_LOG
logging.config.dictConfig(WTSTAMP_LOG)