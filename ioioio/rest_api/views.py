from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from .graph import Graph
from django.http import HttpResponse
from rest_framework.response import Response
from .maps import staty, patch_test, avg_time
from .models import Station, Email
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

    x1, y1 = Graph.get_coords(request.GET.get('station_a'))
    x2, y2 = Graph.get_coords(request.GET.get('station_b'))

    print(id_a, id_b)
    path = Graph.compute_path(id_a, id_b)
    path = Graph.add_start(path, x1, y1)
    path = Graph.add_end(path, x2, y2)
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


@csrf_exempt
@api_view(['POST'])
def register_email(request):
    topic = request.POST['topic']
    first_name = request.POST['firstName']
    second_name = request.POST['secondName']
    email = request.POST['email']
    content = request.POST['content']
    try:
        new_email = Email(topic=topic,
                          first_name=first_name,
                          second_name=second_name,
                          email=email,
                          content=content)
        new_email.save()
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_201_CREATED)
