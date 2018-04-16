# Create your views here.
from .models import Station
from .path import compute_path
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
    a = Station.objects.filter(id=a_id)[0]
    b = Station.objects.filter(id=b_id)[0]

    path = compute_path(a, b)
    print(path)
    return Response(path)
