import datetime
import re
import time
from multiprocessing import Lock
from .models import Station, Path
from collections import defaultdict
from django.forms import model_to_dict
from decimal import Decimal, InvalidOperation
from .nextbike import NextbikeCache

# one has to wait 2 minutes before using Veturilo after putting back the bicycle
STATION_LAG = 180
CHANGE_LAG = 60
TIME_THRESHOLD = 1200

QUERY_STRING_REGEX = re.compile('^(\d\d(\.\d+)?)\|(\d\d(\.\d+)?)$')


class Graph:
    lock = Lock()

    @staticmethod
    def _refresh_graph():
        Graph._nodes = set()
        Graph._edges = defaultdict(list)
        Graph._times = {}
        Graph._lengths = {}
        Graph._stations = dict(map(lambda d: (d['id'], (d['name'], d['latitude'], d['longitude'])),
                                   (map(lambda el: model_to_dict(el),
                                        Station.objects.all()))))
        Graph._paths = dict(map(lambda d: ((d['station_a'], d['station_b']), (d['time'], d['length'])),
                                map(lambda el: model_to_dict(el),
                                    Path.objects.all())))

        Graph._stations_with_bike = set(NextbikeCache.stations_with_bike())

        for id, _ in Graph._stations.items():
            Graph._add_node(id)

        for (id_a, id_b), (t, length) in Graph._paths.items():
            Graph._add_edge(id_a, id_b, t, length)

        Graph._last_edit = time.time()

    @staticmethod
    def _add_node(station):
        Graph._nodes.add(station)

    @staticmethod
    def _add_edge(a, b, time, length):
        if time <= TIME_THRESHOLD:
            Graph._edges[a].append(b)
            Graph._edges[b].append(a)
            Graph._lengths[(a, b)] = length
            Graph._lengths[(b, a)] = length
            Graph._times[(a, b)] = time + CHANGE_LAG if a in Graph._stations_with_bike else time + STATION_LAG
            Graph._times[(b, a)] = time + CHANGE_LAG if b in Graph._stations_with_bike else time + STATION_LAG

    @staticmethod
    def _dijkstra(source):
        visited = {source: 0}
        path = {source: source}
        nodes = set(Graph._nodes)

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

            for node in Graph._edges[min_node]:
                weight = current_weight + Graph._times[(min_node, node)]
                if node not in visited or weight < visited[node]:
                    visited[node] = weight
                    path[node] = min_node

        return path

    @staticmethod
    def compute_path(station_a, station_b):
        tree = Graph._dijkstra(station_a)
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
                eta += Graph._times[path[i - 1], id]
                total_length += Graph._lengths[path[i - 1], id]
            name, lat, lon = Graph._stations[id]
            result.append({
                'name': name,
                'longitude': lon,
                'latitude': lat,
                'ETA': eta,
                'length': total_length
            })

        return result

    @staticmethod
    def get_id_or_none(qs_value):
        if QUERY_STRING_REGEX.match(qs_value):
            (x, _, y, _) = QUERY_STRING_REGEX.match(qs_value).groups()
            try:
                latitude, longitude = Decimal(x), Decimal(y)
            except InvalidOperation:
                return None

            Graph.lock.acquire()
            if not hasattr(Graph, '_last_edit') or time.time() - Graph._last_edit > datetime.timedelta(minutes=1).total_seconds():
                Graph._refresh_graph()
            Graph.lock.release()

            dist = 100
            result = None

            for id, (_, lat, lon) in Graph._stations.items():
                if id in Graph._stations_with_bike:
                    tmp = float((latitude - Decimal(lat)) ** Decimal(2) + (longitude - Decimal(lon)) ** Decimal(2))
                    if dist > tmp:
                        dist = tmp
                        result = id

            return result
        else:
            return None
