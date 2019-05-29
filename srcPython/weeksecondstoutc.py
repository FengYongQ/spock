def weeksecondstoutc(gpsweek,gpsseconds,leapseconds):
    import datetime, calendar
    datetimeformat = "%Y-%m-%d %H:%M:%S"
    epoch = datetime.datetime.strptime("1980-01-06 00:00:00",datetimeformat)
    elapsed = datetime.timedelta(days=(gpsweek*7),seconds=(gpsseconds+leapseconds))
    return datetime.datetime.strftime(epoch + elapsed,datetimeformat)


