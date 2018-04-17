from .models import Station, Path
from collections import defaultdict
from django.forms import model_to_dict

# one has to wait 2 minutes before using Veturilo after putting back the bicycle
STATION_LAG = 120
DISTANCE_THRESHOLD = 1200
STATIONS = dict(map(lambda d: (d['id'], (d['name'], d['latitude'], d['longitude'])),
                    (map(lambda el: model_to_dict(el),
                         Station.objects.all()))))
PATHS = dict(map(lambda d: ((d['station_a'], d['station_b']), d['time']),
                 map(lambda el: model_to_dict(el),
                     Path.objects.all())))

class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, station):
        self.nodes.add(station)

    def add_edge(self, a, b, distance):
        if distance <= DISTANCE_THRESHOLD:
            self.edges[a].append(b)
            self.edges[b].append(a)
            self.distances[(a, b)] = distance + STATION_LAG
            self.distances[(b, a)] = distance + STATION_LAG

def station_graph():
    result = Graph()

    for id, _ in STATIONS.items():
        result.add_node(id)

    for (id_a, id_b), time in PATHS.items():
        result.add_edge(id_a, id_b, time)

    return result

GRAPH = station_graph()

def dijsktra(source):
    visited = {source: 0}
    path = {source: source}

    nodes = set(GRAPH.nodes)

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

        for node in GRAPH.edges[min_node]:
            weight = current_weight + GRAPH.distances[(min_node, node)]
            if node not in visited or weight < visited[node]:
                visited[node] = weight
                path[node] = min_node

    return path

def compute_path(station_a, station_b):
    tree = dijsktra(station_a)
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
            eta += GRAPH.distances[path[i-1], path[i]]
        name, lon, lat = STATIONS[id]
        result.append({
            'name': name,
            'longitude': lon,
            'latitude': lat,
            'ETA': eta - STATION_LAG if i else 0
        })

    return result
