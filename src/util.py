import datetime

def dt2str(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def d2str(dt):
    return dt.strftime("%Y-%m-%d")

def str2dt(s):
    return datetime.datetime.fromisoformat(s) # %Y-%m-%d %H:%M:%S

def epoch_to_datetime(epoch):
    return datetime.datetime.fromtimestamp(epoch)
