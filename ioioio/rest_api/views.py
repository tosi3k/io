from rest_framework import status

from .graph import Graph
from django.http import HttpResponse
from rest_framework.response import Response
from .maps import staty, patch_test, avg_time
from .models import Station
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, renderer_classes


# do testów
def call_staty(request):
    staty(50)


def call_test(request):
    records, requests = patch_test()
    response = "Records %d, requests %d" % (records, requests)
    return HttpResponse(response)


def call_avg(requests):
    avg, max = avg_time()
    response = "avg %f min, max %f min" % (avg/60, max/60)
    return HttpResponse(response)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def dijkstra(request):
    id_a = Graph.get_id_or_none(request.GET.get('station_a'))
    id_b = Graph.get_id_or_none(request.GET.get('station_b'))
    if not id_a or not id_b:
        return Response({'Error': 'Failed to parse the query string'}, status=status.HTTP_404_NOT_FOUND)
    print(id_a, id_b)
    path = Graph.compute_path(id_a, id_b)
    print(path)
    return Response(path)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def stations(request):
    stations = []

    for station in Station.objects.all().order_by('name'):
        stations.append({
            'name': station.name,
            'lat': float(station.latitude),
            'lon': float(station.longitude)
        })

    return Response({'stations': stations})
