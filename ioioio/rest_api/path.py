from .models import Station, Path
from collections import defaultdict

class Graph:
    def __init__(self):
        self.nodes = set(Station)
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, station):
        self.nodes.add(station)

    def add_edge(self, a, b, distance):
        self.edges[a].append(b)
        self.edges[b].append(a)
        self.distances[(a, b)] = distance
        self.distances[(b, a)] = distance

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

def dijsktra(graph, source):
    visited = {source: 0}
    path = {source: source}

    nodes = set(graph.nodes)

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

        for node in graph.edges[min_node]:
            weight = current_weight + graph.distances[(min_node, node)]
            if node not in visited or weight < visited[node]:
                visited[node] = weight
                path[node] = min_node

    return path

def compute_path(station_a, station_b):
    graph = station_graph()
    path = dijsktra(graph, station_a)
    result = []
    node = station_b

    while node != station_a:
        result.insert(0, node)
        node = path[node]

    result.insert(0, station_a)
    return path
