#   Class that simplifies time operations
#

import pytz
import time
import datetime

class TimeHelper():
    def __init__(self):
        pass

    # datetime.strptime() class method creates a datetime object from a string representing a date and time and a corresponding format string
    # timetuple() -> return a time.struct_time such as returned by time.localtime()
    # mktime() -> returns the Unix timestamp corresponding to the arguments given
    # input str in format "%Y-%m-%d %H:%M" (eg: 2018-09-05 07:00)
    def timeStrToTimestamp(self, s, fmt="%Y-%m-%d %H:%M"):
        return time.mktime(datetime.datetime.strptime(s, fmt).timetuple())

    def timeStringToDatetime(self, s, fmt="%Y-%m-%d %H:%M"):
        return datetime.datetime.strptime(s, fmt)

    # t1 > t2 -> 1
    # t1 == t2 -> 0
    # t1 < t2 -> -1
    def compareTimes(self, t1, t2):
        ts1 = self.timeStrToTimestamp(t1)
        ts2 = self.timeStrToTimestamp(t2)

        if ts1 > ts2:
            return 1
        elif ts1 == ts2:
            return 0
        else:
            return -1

    def getTimeByTimezone(self, fmt='%Y-%m-%d %H:%M', tzstring='Asia/Singapore'):
        try:
            tz = pytz.timezone(tzstring)
            return datetime.datetime.now(tz)
        except Exception:
            return None

    # ascending sort
    # index of date value in two dimensional array
    def sortArrayByDateEx(self, dates, index=0, fmt="%Y-%m-%d %H:%M"):
        dates.sort(key=lambda d:datetime.datetime.strptime(d[index], fmt))
        return dates

