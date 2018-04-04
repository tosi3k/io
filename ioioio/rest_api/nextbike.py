import urllib.request
from .models import Station
import xml.etree.ElementTree as ET

NEXTBIKE_URL = 'http://api.nextbike.net/maps/nextbike-official.xml?city=210'

def nextbike_xml():
    xml_contents = urllib.request.urlopen(NEXTBIKE_URL).read()
    tree = ET.fromstring(xml_contents)
    return tree

def stations_with_bike():
    xml = nextbike_xml()
    names = []
    for place in xml[0][0]:
        if int(place.attrib['bikes']):
            names.append(place.attrib['name'])
    return Station.objects.filter(name__in=names)

# def import_stations():
#     xml = nextbike_xml()
#     for place in xml[0][0]:
#         s = Station(name=place.attrib['name'],
#                     latitude=place.attrib['lat'],
#                     longitude=place.attrib['lng'])
#         s.save()
