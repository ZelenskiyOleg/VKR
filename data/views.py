import os

#import face_recognition
from PIL import Image
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from data.handlers import detect_faces, journal_find
from data.models import Data
from data.serializers import UsersSerializer


class UsersListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        serializer = UsersSerializer(Data.objects.all(), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        try:
            if request.FILES.get('photo'):
                photo = request.FILES['photo']
                result = Data.objects.create(username=request.POST.get('username'),
                                             first_name=request.POST.get('first_name'),
                                             last_name=request.POST.get('last_name'),
                                             group=request.POST.get('group'),
                                             photo=photo)
            else:
                if request.POST.get('update'):
                    user = Data.objects.get(username=request.POST.get('old_username'))
                    user.username = request.POST.get('username')
                    user.save()
                    return Response(status=status.HTTP_201_CREATED)
                else:
                    result = Data.objects.create(username=request.POST.get('username'),
                                                 first_name=request.POST.get('first_name'),
                                                 last_name=request.POST.get('last_name'),
                                                 group=request.POST.get('group'))
            return Response({'result': f'User: {result.username} is created'})
        except:
            return Response({'result': 'Something went wrong!'})

@api_view(['POST'])
def journal(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        userid = request.POST.get('userid', False)
        print(date)
        text = journal_find(date, userid)
        return Response({'result': text})
    return Response({'result': 'Something went wrong!'})


@api_view(['POST'])
def receive_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        photo = request.FILES['photo']
        folder = os.path.join(settings.BASE_DIR, 'temp_img')
        userid = request.POST.get('userid', None)

        for file_name in os.listdir(folder):
            file_path = os.path.join(folder, file_name)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

        fs = FileSystemStorage(location=folder)
        filename = fs.save(photo.name, photo)
        file_path = fs.path(filename)
        print(file_path)
        output_folder = "/Users/zelenol/Documents/VKRProject/buf_img"
        print(userid)
        response = detect_faces(file_path, output_folder, userid)

        print(response)
        return Response({'result': response})
