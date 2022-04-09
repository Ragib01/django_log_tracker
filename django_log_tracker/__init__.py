r"""
 ____   _                              _                  _____                   _               
|  _ \ (_)  __ _  _ __    __ _   ___  | |     ___    __ _|_   _|_ __  __ _   ___ | | __ ___  _ __ 
| | | || | / _` || '_ \  / _` | / _ \ | |    / _ \  / _` | | | | '__|/ _` | / __|| |/ // _ \| '__|
| |_| || || (_| || | | || (_| || (_) || |___| (_) || (_| | | | | |  | (_| || (__ |   <|  __/| |   
|____/_/ | \__,_||_| |_| \__, | \___/ |_____|\___/  \__, | |_| |_|   \__,_| \___||_|\_\\___||_|   
     |__/                |___/                      |___/                                        

"""

import os
from .events import Events

if os.environ.get('RUN_MAIN', None) != 'true':
    default_app_config = 'django_log_tracker.apps.DjangoLogTrackerConfig'

LOG_TRACKER_SIGNAL = Events()

__title__ = 'Django Log Tracker'
__version__ = '1.0.3'
__author__ = 'Ragib Shahriar'
__license__ = 'MIT LICENSE'
__copyright__ = 'Copyright 2022 Ragib Shahriar'

# Version synonym
VERSION = __version__
