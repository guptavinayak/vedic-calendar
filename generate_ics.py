import datetime
import math
from icalendar import Calendar, Event

PUNE_LAT = 18.5204
PUNE_LON = 73.8567
PROHIBITED_TITHIS = {8, 14, 15, 30}  # Ashtami, Chaturdashi, Purnima, Amavasya
ALLOWED_WEEKDAYS = {2, 4}             # Wed (2), Fri (4)
TITHI_NAMES = {
    1: 'Shukla Pratipada', 2: 'Shukla Dwitiya', 3: 'Shukla Tritiya',
    4: 'Shukla Chaturthi', 5: 'Shukla Panchami', 6: 'Shukla Shashthi',
    7: 'Shukla Saptami', 8: 'Shukla Ashtami', 9: 'Shukla Navami',
    10: 'Shukla Dashami', 11: 'Shukla Ekadashi', 12: 'Shukla Dwadashi',
    13: 'Shukla Trayodashi', 14: 'Shukla Chaturdashi', 15: 'Purnima',
    16: 'Krishna Pratipada', 17: 'Krishna Dwitiya', 18: 'Krishna Tritiya',
    19: 'Krishna Chaturthi', 20: 'Krishna Panchami', 21: 'Krishna Shashthi',
    22: 'Krishna Saptami', 23: 'Krishna Ashtami', 24: 'Krishna Navami',
    25: 'Krishna Dashami', 26: 'Krishna Ekadashi', 27: 'Krishna Dwadashi',
    28: 'Krishna Trayodashi', 29: 'Krishna Chaturdashi', 30: 'Amavasya',
}

# Tithi observances are independent of the weekday grooming windows. The
# approximate model cannot identify regional festival names reliably, but it
# can still expose every occurrence of these recurring observances.
TITHI_OBSERVANCES = {
    11: 'Ekadashi (Shukla Paksha)',
    26: 'Ekadashi (Krishna Paksha)',
    23: 'Kalashtami (Krishna Ashtami)',
    14: 'Chaturdashi (Shukla Paksha)',
    29: 'Chaturdashi (Krishna Paksha)',
}

def approximate_tithi(dt):
    # Reference epoch: Jan 6, 2000, 18:14 UTC (Known New Moon)
    epoch = datetime.datetime(2000, 1, 6, 18, 14)
    diff_days = (dt - epoch).total_seconds() / 86400.0
    synodic_month = 29.53058867
    phase = (diff_days % synodic_month) / synodic_month
    tithi = math.floor(phase * 30) + 1
    return int(tithi)

def add_all_day_event(cal, day, summary, description):
    event = Event()
    event.add('summary', summary)
    event.add('dtstart', day)
    event.add('dtend', day + datetime.timedelta(days=1))
    event.add('description', description)
    event.add('location', 'Pune, Maharashtra, India')
    cal.add_component(event)

def build_feed():
    cal = Calendar()
    cal.add('prodid', '-//Vedic Kshoura Karma Calendar//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Vedic Grooming Windows')

    start = datetime.date.today()
    # Project forward 180 days
    for i in range(180):
        day = start + datetime.timedelta(days=i)
        check_time = datetime.datetime.combine(day, datetime.time(9, 30))
        tithi = approximate_tithi(check_time)

        if tithi in TITHI_OBSERVANCES:
            name = TITHI_OBSERVANCES[tithi]
            add_all_day_event(
                cal,
                day,
                name,
                f'{name}. Approximate tithi: {TITHI_NAMES[tithi]}. '
                'Confirm the local sunrise-based date before observing.',
            )

        if day.weekday() not in ALLOWED_WEEKDAYS:
            continue

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