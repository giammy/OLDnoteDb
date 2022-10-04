import os
import logging
from datetime import datetime
from socketserver import ThreadingUnixStreamServer
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.conf import settings

from rest_framework.parsers import JSONParser 
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import viewsets
# from rest_framework.response import Response

from note.models import Note
from note.serializers import NoteSerializer
from note.serializers import FileSerializer

# Create your views here.
def index(request):
    return HttpResponse("Note view.")

#
# API
#

# i.e. python3 manage.py runserver 0:8080
# i.e. http://localhost:8080/note/api/note

def createNote(note_data):
    # note_data is a Json text
    note_serializer = NoteSerializer(data=note_data)
    if note_serializer.is_valid():
        note_serializer.save()
        # print("xxx: ", note_serializer.data)
        return note_serializer.data, status.HTTP_201_CREATED
    return note_serializer.errors, status.HTTP_400_BAD_REQUEST

@api_view(['GET', 'POST'])
def noteListCreate(request):
    if request.method == 'GET':
        logging.info("noteListCreate: GET")
        notes = Note.objects.all()
        
        id = request.query_params.get('id', None)
        if id is not None:
            notes = notes.filter(id__icontains=id)
        
        note_serializer = NoteSerializer(notes, many=True)
        return JsonResponse(note_serializer.data, safe=False)
        # 'safe=False' for objects serialization
 
    elif request.method == 'POST':
        logging.info("noteListCreate: POST")
        note_data = JSONParser().parse(request)
        # print(note_data) # {'rid': 1, 'lid': 1, 'type': 'test', 'data': 'test'}
        retData, stts = createNote(note_data)
        return JsonResponse(retData, status=stts) 

@api_view(['GET', 'PUT', 'DELETE'])
def noteDetail(request, id):
    try:
        note = Note.objects.get(id=id)
    except Note.DoesNotExist:
        return JsonResponse({'message': 'The note does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        note_serializer = NoteSerializer(note)
        return JsonResponse(note_serializer.data)

    elif request.method == 'PUT': 
        note_data = JSONParser().parse(request) 
        note_serializer = NoteSerializer(note, data=note_data) 
        if note_serializer.is_valid(): 
            note_serializer.save() 
            return JsonResponse(note_serializer.data) 
        return JsonResponse(note_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
 
    elif request.method == 'DELETE': 
        note.delete() 
        return JsonResponse({'message': 'Note was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def noteSearch(request):
    
    id = request.GET.get('id', None)
    rid = request.GET.get('rid', None)
    lid = request.GET.get('lid', None)
    type = request.GET.get('type', None)
    data = request.GET.get('data', None)
 
    # create a dictionary with nonull values                                                                              
    search_dict = {k: v for k, v in {'id': id, 
                   'rid': rid, 'lid': lid, 
                   'type': type, 'data': data}.items() if v is not None}

    # search_dict = {k: v for k, v in {'id'+'__icontains': id, 
    #                'rid'+'__icontains': rid, 'lid'+'__icontains': lid, 
    #                'type'+'__icontains': type, 'data'+'__icontains': data}.items() if v is not None}
    notes = Note.objects.filter(**search_dict).all()

    note_serializer = NoteSerializer(notes, many=True)
    return JsonResponse(note_serializer.data, safe=False)

@api_view(['GET'])
def noteiSearch(request):
    
    id = request.GET.get('iid', None)
    rid = request.GET.get('irid', None)
    lid = request.GET.get('ilid', None)
    type = request.GET.get('itype', None)
    data = request.GET.get('idata', None)
    
    # create a dictionary with nonull values                                                                              
    search_dict = {k: v for k, v in {'id'+'__icontains': id, 
                   'rid'+'__icontains': rid, 'lid'+'__icontains': lid, 
                   'type'+'__icontains': type, 'data'+'__icontains': data}.items() if v is not None}
    notes = Note.objects.filter(**search_dict).all()

    note_serializer = NoteSerializer(notes, many=True)
    return JsonResponse(note_serializer.data, safe=False)

@api_view(['GET'])
def noteQuery(request):
    
    id = request.GET.get('id', None)
    rid = request.GET.get('rid', None)
    lid = request.GET.get('lid', None)
    type = request.GET.get('type', None)
    data = request.GET.get('data', None)
 
    iid = request.GET.get('iid', None)
    irid = request.GET.get('irid', None)
    ilid = request.GET.get('ilid', None)
    itype = request.GET.get('itype', None)
    idata = request.GET.get('idata', None)

    # create a dictionary with nonull values                                                                              
    search_dict = {k: v for k, v in {'id': id, 
                   'rid': rid, 'lid': lid, 
                   'type': type, 'data': data}.items() if v is not None}
    search_idict = {k: v for k, v in {'id'+'__icontains': iid, 
                    'rid'+'__icontains': irid, 'lid'+'__icontains': ilid, 
                    'type'+'__icontains': itype, 'data'+'__icontains': idata}.items() if v is not None}
    search_merged = {**search_dict, **search_idict}
    notes = Note.objects.filter(**search_merged).all()

    note_serializer = NoteSerializer(notes, many=True)
    return JsonResponse(note_serializer.data, safe=False)

#
# file upload management
#

class FileUploadViewSet(viewsets.ViewSet):

    def create(self, request):
        serializer_class = FileSerializer(data=request.data)
        if 'file' not in request.FILES or not serializer_class.is_valid():
            return JsonResponse({'status': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        else:
            uniqueFilename = save_to_disk_uploaded_file(request.FILES['file'])

            # create a __FILE__ note
            retData1, status1 = createNote({'rid': 0, 'lid': 0, 'type': '__FILE__', 'data': "__ENT__"})
            if status1 == status.HTTP_400_BAD_REQUEST:
                return JsonResponse(retData1, status=status.HTTP_400_BAD_REQUEST)
            fileNoteID = retData1['id']
            # create a FILENAME note as attribute of __FILE__
            retData2, status2 = createNote({'rid': fileNoteID, 'lid': 0, 'type': 'FILENAME', 'data': request.FILES['file'].name})
            # create a CONTENTS note as attribute of __FILE__
            retData3, status3 = createNote({'rid': fileNoteID, 'lid': 0, 'type': 'CONTENTS', 'data': uniqueFilename})
            return JsonResponse(retData1, status=status1)
            # return Response(status=status.HTTP_201_CREATED)

def save_to_disk_uploaded_file(f):
    # writing file to disk will put it in the project root directory
    # print(f.name, f.size, f.content_type, f.charset, f.content_type_extra)
    currentDateTime = datetime.now(timezone.utc) 
    timeStamp = currentDateTime.strftime("%Y%m%dT%H%M%SZ") + str(currentDateTime.microsecond//1000).zfill(3)
    #print(timeStamp)
    theName = settings.FILES_DIRECTORY + '/' + timeStamp + '-' + f.name
    with open(theName, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return theName

@api_view(['GET'])
def noteDownload(request, id):
    logging.info("noteDownload: id = " + str(id))
    try:
        note = Note.objects.get(id=id)
    except Note.DoesNotExist:
        return JsonResponse({'message': 'The note does not exist'}, status=status.HTTP_404_NOT_FOUND)

    # MITICO (the whole if)!
    if note.type == '__FILE__':
        # get the filename
        filename = Note.objects.get(rid=id, type='FILENAME').data
        # get the contents
        contents = Note.objects.get(rid=id, type='CONTENTS').data
        # read the file
        with open(contents, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(filename)
            return response
    