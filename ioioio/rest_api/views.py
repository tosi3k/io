# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_hello_world(request):
    return Response({
        'hello2': 'world2',
        'hello1': 'world1',
    })
