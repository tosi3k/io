# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from .maps import staty, patch_test, avg_time
from .models import Station
from .path import compute_path

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

def call_dijkstra(requests, a_id, b_id):
    a = Station.objects.filter(id = a_id)
    b = Station.objects.filter(id = b_id)

    print(compute_path(a, b))
    return HttpResponse("DONE")
