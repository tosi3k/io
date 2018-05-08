# Create your views here.
from rest_framework import status

from .path import compute_path, get_id_or_none
from django.http import HttpResponse
from rest_framework.response import Response
from .maps import staty, patch_test, avg_time
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, renderer_classes

@api_view(['GET'])
def api_hello_world(request):
    return Response({
        'hello2': 'world2',
        'hello1': 'world1',
    })

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
def call_dijkstra(request, a_id, b_id):
    path = compute_path(a_id, b_id)
    print(path)
    return Response(path)

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def dijkstra(request):
    id_a = get_id_or_none(request.GET.get('station_a'))
    id_b = get_id_or_none(request.GET.get('station_b'))
    if not id_a or not id_b:
        return Response({'Error': 'Failed to parse the query string'}, status=status.HTTP_404_NOT_FOUND)
    print(id_a, id_b)
    path = compute_path(id_a, id_b)
    print(path)
    return Response(path)
