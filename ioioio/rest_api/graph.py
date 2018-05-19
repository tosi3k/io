from decimal import Decimal, InvalidOperation
from .models import Station, Path
from collections import defaultdict
from django.forms import model_to_dict

# one has to wait 2 minutes before using Veturilo after putting back the bicycle
STATION_LAG = 120
DISTANCE_THRESHOLD = 1200

# TODO further cleanup

class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}
        self._STATIONS = dict(map(lambda d: (d['id'], (d['name'], d['latitude'], d['longitude'])),
                                  (map(lambda el: model_to_dict(el),
                                       Station.objects.all()))))
        self._PATHS = dict(map(lambda d: ((d['station_a'], d['station_b']), d['time']),
                               map(lambda el: model_to_dict(el),
                                   Path.objects.all())))

        for id, _ in self._STATIONS.items():
            self._add_node(id)

        for (id_a, id_b), time in self._PATHS.items():
            self._add_edge(id_a, id_b, time)

    def _add_node(self, station):
        self.nodes.add(station)

    def _add_edge(self, a, b, distance):
        if distance <= DISTANCE_THRESHOLD:
            self.edges[a].append(b)
            self.edges[b].append(a)
            self.distances[(a, b)] = distance + STATION_LAG
            self.distances[(b, a)] = distance + STATION_LAG

    def stations(self):
        return self._STATIONS

    def _dijkstra(self, source):
        visited = {source: 0}
        path = {source: source}

        nodes = set(self.nodes)

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

            for node in self.edges[min_node]:
                weight = current_weight + self.distances[(min_node, node)]
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
        for i in range(len(path)):
            id = path[i]
            if i:
                eta += self.distances[path[i-1], path[i]]
            name, lon, lat = self._STATIONS[id]
            result.append({
                'name': name,
                'longitude': lon,
                'latitude': lat,
                'ETA': eta - STATION_LAG if i else 0
            })

        return result

    def get_id_or_none(self, qs_value):

        if qs_value[0].isdigit():
            coords = qs_value.split('|')
            if len(coords) != 2:
                return None
            try:
                latitude, longitude = Decimal(coords[0]), Decimal(coords[1])
            except InvalidOperation:
                return None

            dist = 100
            result = None
            for id, (_, lat, lon) in self._STATIONS.items():
                tmp = float((latitude - Decimal(lat)) ** Decimal(2) + (longitude - Decimal(lon)) ** Decimal(2))
                if dist > tmp:
                    dist = tmp
                    result = id

            return result
        else:
            for id, (name, _, _) in self._STATIONS.items():
                if name == qs_value:
                    return id
            return None
