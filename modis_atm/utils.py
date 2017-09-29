

def date_diff(overpass_date, target_date):
    try:
        return overpass_date - target_date
    except TypeError:
        overpass_date = overpass_date.replace(tzinfo=None)
        target_date = target_date.replace(tzinfo=None)
        return overpass_date - target_date


def average_datetime(date1, date2):
    dt = date_diff(date1, date2)
    date = date1 + dt / 2
    return date
