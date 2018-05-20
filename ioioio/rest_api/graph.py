import re
from .models import Station, Path
from collections import defaultdict
from django.forms import model_to_dict
from decimal import Decimal, InvalidOperation
from .nextbike import NextbikeCache

# one has to wait 2 minutes before using Veturilo after putting back the bicycle
STATION_LAG = 120
TIME_THRESHOLD = 1200

QUERY_STRING_REGEX = re.compile('^(\d\d(\.\d+)?)\|(\d\d(\.\d+)?)$')

# TODO implement nextbike interface with atomic caching of the XML file (w/ a timestamp)
# maybe cache the graph structure as well?

class Graph:
    def __init__(self):
        self._nodes = set()
        self._edges = defaultdict(list)
        self._times = {}
        self._lengths = {}
        self._stations = dict(map(lambda d: (d['id'], (d['name'], d['latitude'], d['longitude'])),
                                  (map(lambda el: model_to_dict(el),
                                       Station.objects.all()))))
        self._paths = dict(map(lambda d: ((d['station_a'], d['station_b']), (d['time'], d['length'])),
                               map(lambda el: model_to_dict(el),
                                   Path.objects.all())))

        self._stations_with_bike = set(NextbikeCache.stations_with_bike())

        for id, _ in self._stations.items():
            self._add_node(id)

        for (id_a, id_b), (time, length) in self._paths.items():
            self._add_edge(id_a, id_b, time, length)

    def _add_node(self, station):
        self._nodes.add(station)

    def _add_edge(self, a, b, time, length):
        if time <= TIME_THRESHOLD:
            self._edges[a].append(b)
            self._edges[b].append(a)
            self._lengths[(a, b)] = length
            self._lengths[(b, a)] = length
            self._times[(a, b)] = time if a in self._stations_with_bike else time + STATION_LAG
            self._times[(b, a)] = time if b in self._stations_with_bike else time + STATION_LAG

    def _dijkstra(self, source):
        visited = {source: 0}
        path = {source: source}
        nodes = set(self._nodes)

        while nodes:
            min_node = None

            for node in nodes:
                if node in visited:
                    if not min_node:
                        min_node = node
                    elif visited[node] < visited[min_node]:
                        min_node = node

            if not min_node:
                break

            nodes.remove(min_node)
            current_weight = visited[min_node]

            for node in self._edges[min_node]:
                weight = current_weight + self._times[(min_node, node)]
                if node not in visited or weight < visited[node]:
                    visited[node] = weight
                    path[node] = min_node

        return path

    def compute_path(self, station_a, station_b):
        tree = self._dijkstra(station_a)
        path = []
        result = []

        node = station_b
        while node != station_a:
            path.insert(0, node)
            node = tree[node]
        path.insert(0, station_a)

        eta = 0
        total_length = 0
        for i in range(len(path)):
            id = path[i]
            if i:
                eta += self._times[path[i - 1], id]
                total_length += self._lengths[path[i - 1], id]
            name, lon, lat = self._stations[id]
            result.append({
                'name': name,
                'longitude': lon,
                'latitude': lat,
                'ETA': eta,
                'length': total_length
            })

        return result

    def get_id_or_none(self, qs_value):
        if QUERY_STRING_REGEX.match(qs_value):
            (x, _, y, _) = QUERY_STRING_REGEX.match(qs_value).groups()
            try:
                latitude, longitude = Decimal(x), Decimal(y)
            except InvalidOperation:
                return None

            dist = 100
            result = None
            for id, (_, lat, lon) in self._stations.items():
                # TODO consider only the stations with bike(s)
                tmp = float((latitude - Decimal(lat)) ** Decimal(2) + (longitude - Decimal(lon)) ** Decimal(2))
                if dist > tmp:
                    dist = tmp
                    result = id

            return result
        else:
            return None
