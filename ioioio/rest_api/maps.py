from datetime import datetime
from decimal import *
import random
import googlemaps
import json

from .models import Station, Path
from django.db.models import Max, Avg

import pprint

MAX_COUNT = 25
MAX_DISTANCE = 0.06  #0.05 is around 20 min riding

def patch_test():
    records, requests = patch(Station.objects.all()[0])
    print("Added %d records, send %d requests" % (records, requests))
    return records, requests

def patch_all(key_num = 0):
    records = 0
    requests = 0
    i = 0
    with open('api_keys.json', 'r') as keys_f:
        keys = json.load(keys_f)["keys"]
    for station in Station.objects.all():
        i += 1
        rec, req = patch(station, keys[key_num])
        print("Computed %d stations, saved  %d records, send %d requests so far" % (i, records, requests))
        records += rec
        requests += req

    return records, requests

def patch(station, key):
    destinations = []
    for b in Station.objects.all():
        if b != station and \
        len(Path.objects.filter(station_a = station, station_b = b)) == 0 and \
        map_distance(station, b) < Decimal(MAX_DISTANCE):
            destinations.append(b)

    records, requests = compute_paths(station, destinations, key, max_count = 25)
    return records, requests

def map_distance(a, b):
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
    for p in range(len(groups)):
        now = datetime.now()
        if len(groups[p][1]) > 0:
            directions_result = gmaps.distance_matrix(get_cords(origin), groups[p][1],
                                                      mode="bicycling",
                                                      departure_time=now)
            requests += len(groups[p][1])
            # print('request succes')
            times = directions_result['rows']
            for i in range(len(groups[p][1])):
                row = times[0]['elements']
                time = row[i]['duration']['value']
                if time > max_time:
                    print("More than hour")
                records += 2
                add_path(origin, groups[p][0][i], time)
    return records, requests

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

def add_path(s_a, s_b, time):
    path = Path(station_a = s_a,
    station_b = s_b,
    time = time)
    path.save()
    path = Path(station_a = s_b,
    station_b = s_a,
    time = time)
    path.save()

def get_cords(station):
    latitude  = getattr(station, 'latitude')
    longitude = getattr(station, 'longitude')
    return latitude + ', ' + longitude

#### EVERYTHING BELOW UNDER DEVELOPMENT OR FOR TEST PURPOSE ####

# def compute_all_paths(max_count = MAX_COUNT, max_time = 60*60):
#     gmaps = googlemaps.Client(key = GOOGLE_API_KEY)
#     groups = group_stations(max_count)
#
#     #for testing and safety
#     # pp = pprint.PrettxyPrinter()
#     groups = groups[:1]
#     # pp.pprint(groups)
#
#     for p in range(len(groups)):
#         for q in range(i, len(groups)):
#             now = datetime.now()
#             directions_result = gmaps.distance_matrix(groups[p][1], groups[q][1], #from, to
#                                                       mode="bicycling",
#                                                       departure_time=now)
#             req_time = datetime.now()
#             count = 0
#             print('request succes')
#             times = directions_result['rows']
#             for i in range(len(groups[p][1])):
#                 row = times[i]['elements']
#                 for j in range(len(groups[q][1])):
#                     time = row[j]['duration']['value']
#                     if time != 0 and time <= max_time:
#                         count += 2
#                         # g1[0][i] != g2[0][j] would be probably better option
#                         # but im not 100% sure how comparison function
#                         # for model objects works
#                         add_path(groups[p][0][i], groups[q][0][j], time)
#             add_time = datetime.now()
#             print("Req time: ", req_time - now, ", Add time: ", add_time - req_time, "Added ", count, " records")
#
# def group_stations(max_count = MAX_COUNT):
#     result = []
#
#     count = 0
#     names = []
#     cords = []
#     for station in Station.objects.all():
#         name      = station #getattr(station, 'name')
#         latitude  = getattr(station, 'latitude')
#         longitude = getattr(station, 'longitude')
#         names.append(name)
#         cords.append(latitude + ', ' + longitude)
#         count += 1
#
#         if count == max_count:
#             result.append((names, cords))
#             names = []
#             cords = []
#             count = 0
#
#     return result

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
