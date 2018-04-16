from .models import Station, Path
from collections import defaultdict
from django.forms import model_to_dict

# one has to wait 2 minutes before using Veturilo after putting back the bicycle
STATION_LAG = 120

class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, station):
        self.nodes.add(station)

    def add_edge(self, a, b, distance):
        self.edges[a].append(b)
        self.edges[b].append(a)
        self.distances[(a, b)] = distance + STATION_LAG
        self.distances[(b, a)] = distance + STATION_LAG

def station_graph():
    result = Graph()

    for station in Station.objects.all():
        result.add_node(station)

    for path in Path.objects.all():
        time = getattr(path, 'time')
        station_a = getattr(path, 'station_a')
        station_b = getattr(path, 'station_b')
        result.add_edge(station_a, station_b, time)

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
        if i:
            eta += GRAPH.distances[path[i-1], path[i]]
        station = model_to_dict(path[i])
        result.append({
            'name': station['name'],
            'longitude': station['longitude'],
            'latitude': station['latitude'],
            'ETA': eta - STATION_LAG if i else 0
        })

    return result
