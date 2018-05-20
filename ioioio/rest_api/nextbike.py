import datetime
import time
import urllib.request

import os

from .models import Station
from multiprocessing import Lock
import xml.etree.ElementTree as ET

NEXTBIKE_URL = 'http://api.nextbike.net/maps/nextbike-official.xml?city=210'
NEXTBIKE_XML = 'nextbike-official.xml'


class NextbikeCache:
    lock = Lock()

    def __init__(self):
        pass

    @staticmethod
    def old_xml():
        return time.time() - os.path.getmtime(NEXTBIKE_XML) > datetime.timedelta(minutes=1).total_seconds()

    @staticmethod
    def nextbike_xml():
        NextbikeCache.lock.acquire()
        if not os.path.isfile(NEXTBIKE_XML) or NextbikeCache.old_xml():
            xml_contents = urllib.request.urlopen(NEXTBIKE_URL).read()
            print('wchodze tutaj')
            tree = ET.fromstring(xml_contents)
            f = open(NEXTBIKE_XML, 'w')
            f.write(xml_contents.decode("utf-8"))
            f.close()
        else:
            print('wchodze tutaj2')
            tree = ET.parse(NEXTBIKE_XML).getroot()
        NextbikeCache.lock.release()
        return tree

    @staticmethod
    def stations_with_bike():
        xml = NextbikeCache.nextbike_xml()
        names = []
        for place in xml[0][0]:
            if int(place.attrib['bikes']):
                names.append(place.attrib['name'])
        return Station.objects.filter(name__in=names).values_list('id', flat=True)
