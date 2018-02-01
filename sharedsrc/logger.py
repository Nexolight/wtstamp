import os
from sharedsrc import yamlsettings as settings

_FORMATERS = {
    'detailed': {
        'format':'%(asctime)s %(levelname)-8s %(name)-45s %(message)s'
    },
    'simple': {
        'format':'%(levelname)-8s %(name)-45s %(message)s'
    },
}

_HANDLERS = {
    'console': {
        'class': 'logging.StreamHandler',
        'level': 'DEBUG',
        'formatter': 'simple',
        'stream': 'ext://sys.stdout',
    },
    'wtstamp_file': {
        'class': 'logging.handlers.RotatingFileHandler',
        'level': 'DEBUG',
        'formatter': 'detailed',
        'filename': os.path.join(settings.get("application_data"),'wtstamp.log'),
        'mode': 'a',
        'maxBytes': 10485760,
        'backupCount': 3,
    }
}

WTSTAMP_LOG={
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': _HANDLERS,
    'formatters':_FORMATERS,
    'loggers': {
        '': {
            'level':'DEBUG',
            'handlers':['wtstamp_file','console']
        }
    }
}

CON_LOG={
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': _HANDLERS,
    'formatters':_FORMATERS,
    'loggers': {
        '': {
            'level':'DEBUG',
            'handlers':['console']
        }
    }
}