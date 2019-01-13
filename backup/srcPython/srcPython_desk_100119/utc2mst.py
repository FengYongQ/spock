from datetime import datetime
from dateutil import tz
from pytz import timezone

# This script converts a time from UTC to Mountain time (MST), taking into account daylight saving time
# input: utc time as a string '%Y-%m-%dT%H:%M:%S'
def utc2mst(utc_str):

    # METHOD 1: Hardcode zones:
    from_zone = tz.gettz('UTC')
    utc = datetime.strptime(utc_str, '%Y-%m-%dT%H:%M:%S')
    utc_ok = utc.replace(tzinfo=from_zone)
    mst = utc_ok.astimezone(timezone('US/Mountain'))
    mst_str = datetime.strftime(mst, '%Y-%m-%dT%H:%M:%S')   
    return mst_str

# # METHOD 1: Hardcode zones:
# from_zone = tz.gettz('UTC')
# to_zone = tz.gettz('MST')


# # utc = datetime.utcnow()
# utc = datetime.strptime('2011-06-21 02:37:21', '%Y-%m-%d %H:%M:%S')

# # Tell the datetime object that it's in UTC time zone since 
# # datetime objects are 'naive' by default
# utc_ok = utc.replace(tzinfo=from_zone)

# # Convert time zone
# #central = utc_ok.astimezone(to_zone)

# # central = timezone('US/Mountain').localize(utc)
# # central = datetime.strftime(central, '%Y-%m-%d %H:%M:%S  %Z%z')

# central = utc_ok.astimezone(timezone('US/Mountain'))
# central = datetime.strftime(central, '%Y-%m-%d %H:%M:%S')

