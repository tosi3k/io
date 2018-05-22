from datetime import datetime
from decimal import *
import random
import googlemaps
import json
from django.db import transaction
from googlemaps.exceptions import Timeout as gmTimeoutExceptions

from .models import Station, Path
from django.db.models import Max, Avg

MAX_COUNT = 25
MAX_DISTANCE = 0.06  #0.05 is around 20 min riding

def patch_test():
    records, requests = patch(Station.objects.all()[0])
    print("Added %d records, send %d requests" % (records, requests))
    return records, requests

@transaction.atomic()
def update_paths(key):
    records = 0
    requests = 0
    i = 0
    for path in Path.objects.all().order_by('last_update'):
        _, _, succes = compute_paths(getattr(path, 'station_a'), [getattr(path, 'station_b')], key)
        if not succes:
            break
        i += 1
        print("Updated path: %d" % (getattr(path, 'id')))
    print("Updated %d paths" % (i))

@transaction.atomic()
def patch_all(key):
    records = 0
    requests = 0
    i = 0
    for station in Station.objects.all():
        i += 1
        rec, req = patch(station, key)
        print("Computed %d stations, saved  %d records, send %d requests so far" % (i, records, requests))
        records += rec
        requests += req

    return records, requests

def patch(station, key):
    destinations = []
    for b in Station.objects.all():
        if b != station and \
        len(Path.objects.filter(station_a = station, station_b = b)) == 0 and \
        lazy_distance(station, b) < Decimal(MAX_DISTANCE):
            destinations.append(b)

    records, requests, _ = compute_paths(station, destinations, key, max_count = 25)
    return records, requests

def lazy_distance(a, b):
    alat = Decimal(getattr(a, 'latitude'))
    alon = Decimal(getattr(a, 'longitude'))
    blat = Decimal(getattr(b, 'latitude'))
    blon = Decimal(getattr(b, 'longitude'))

    return ((alat - blat)**Decimal(2) + (alon - blon)**Decimal(2))**Decimal(0.5)

def compute_paths(origin, destinations, key, max_count = MAX_COUNT, max_time = 60*60):
    gmaps = googlemaps.Client(key = key)
    groups = group_destinations(destinations, max_count)

    records = 0
    requests = 0
    succes = True
    for p in range(len(groups)):
        now = datetime.now()
        if len(groups[p][1]) > 0:
            try:
                directions_result = gmaps.distance_matrix(get_cords(origin), groups[p][1],
                                                    mode="bicycling",
                                                    departure_time=now)
                requests += len(groups[p][1])
                times = directions_result['rows']
                for i in range(len(groups[p][1])):
                    row = times[0]['elements']
                    time = row[i]['duration']['value']
                    length = row[i]['distance']['value']
                    if time > max_time:
                        print("More than hour")
                    records += 2
                    add_path(origin, groups[p][0][i], time, length)

            except gmTimeoutExceptions:
                succes = False

    return records, requests, succes

def group_destinations(destinations, max_count):
    result = []
    objs = []
    cords = []
    count = 0
    for d in destinations:
        cords.append(get_cords(d))
        objs.append(d)
        count += 1

        if count >= max_count:
            result.append((objs, cords))
            objs = []
            cords = []
            count = 0

    result.append((objs, cords))
    return result

def add_path(s_a, s_b, time, length):
    path = Path(station_a = s_a,
                station_b = s_b,
                time = time,
                length = length)
    path.save()
    path = Path(station_a = s_b,
                station_b = s_a,
                time = time,
                length = length)
    path.save()

def get_cords(station):
    latitude  = getattr(station, 'latitude')
    longitude = getattr(station, 'longitude')
    return latitude + ', ' + longitude

#### EVERYTHING BELOW UNDER DEVELOPMENT OR FOR TEST PURPOSE ####

def staty(ile = 20):
    odleglosci = 0
    czasy = 0
    gmaps = googlemaps.Client(key = GOOGLE_API_KEY)

    for i in range(ile):
        odl, czas = porownanie(gmaps)
        odleglosci += odl
        czasy += czas

    print("sredni czas na 1 stopnia w min to: ", (czasy/odleglosci)/60)
    return (czasy/odleglosci)/60

def porownanie(gmaps):
    stations = Station.objects.all()

    a = random.choice(stations)
    b = random.choice(stations)

    distance = ((Decimal(getattr(a, 'latitude')) - Decimal(getattr(b, 'latitude')))**Decimal(2) +
    (Decimal(getattr(a, 'longitude')) - Decimal(getattr(b, 'longitude')))**Decimal(2))**Decimal(1/2)


    a_cords = getattr(a, 'latitude') + ', ' + getattr(a, 'longitude')
    b_cords = getattr(b, 'latitude') + ', ' + getattr(b, 'longitude')
    now = datetime.now()
    directions_result = gmaps.distance_matrix(a_cords, b_cords, #from, to
                                              mode="bicycling",
                                              departure_time=now)
    return distance, directions_result['rows'][0]['elements'][0]['duration']['value']

def avg_time():
    avg = Path.objects.all().aggregate(Avg('time'))
    max = Path.objects.all().aggregate(Max('time'))

    return avg['time__avg'], max['time__max']
