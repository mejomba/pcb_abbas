from rest_framework.views import APIView
from rest_framework.response import Response
from .models import HeaderImage
from .serializers import HeaderImageSerializer


class HeaderImageListView(APIView):
    def get(self, request):
        items = HeaderImage.objects.all()
        serializer = HeaderImageSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)
