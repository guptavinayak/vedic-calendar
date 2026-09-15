import datetime
import math
from icalendar import Calendar, Event

PUNE_LAT = 18.5204
PUNE_LON = 73.8567
PROHIBITED_TITHIS = {8, 14, 15, 30}  # Ashtami, Chaturdashi, Purnima, Amavasya
ALLOWED_WEEKDAYS = {2, 4}             # Wed (2), Fri (4)

def approximate_tithi(dt):
    # Reference epoch: Jan 6, 2000, 18:14 UTC (Known New Moon)
    epoch = datetime.datetime(2000, 1, 6, 18, 14)
    diff_days = (dt - epoch).total_seconds() / 86400.0
    synodic_month = 29.53058867
    phase = (diff_days % synodic_month) / synodic_month
    tithi = math.floor(phase * 30) + 1
    return int(tithi)

def build_feed():
    cal = Calendar()
    cal.add('prodid', '-//Vedic Kshoura Karma Calendar//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Vedic Grooming Windows')

    start = datetime.date.today()
    # Project forward 180 days
    for i in range(180):
        day = start + datetime.timedelta(days=i)
        if day.weekday() not in ALLOWED_WEEKDAYS:
            continue

        check_time = datetime.datetime.combine(day, datetime.time(9, 30))
        tithi = approximate_tithi(check_time)
        if tithi in PROHIBITED_TITHIS:
            continue

        event = Event()
        event.add('summary', 'Vedic Grooming Window (Haircut / Shave / Nails)')
        
        if day.weekday() == 2:  # Wednesday
            dt_start = datetime.datetime.combine(day, datetime.time(9, 30))
            dt_end = datetime.datetime.combine(day, datetime.time(11, 30))
            desc = f'Auspicious Wednesday (Budhavara). Tithi: {tithi}. Concludes before Rahu Kaal (~12:30 PM).'
        else:                   # Friday
            dt_start = datetime.datetime.combine(day, datetime.time(8, 30))
            dt_end = datetime.datetime.combine(day, datetime.time(10, 30))
            desc = f'Auspicious Friday (Shukravara). Tithi: {tithi}. Concludes before Rahu Kaal (~11:00 AM).'

        event.add('dtstart', dt_start)
        event.add('dtend', dt_end)
        event.add('description', desc)
        event.add('location', 'Pune, Maharashtra, India')
        cal.add_component(event)

    with open('feed.ics', 'wb') as f:
        f.write(cal.to_ical())

if __name__ == '__main__':
    build_feed()