from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from rest_framework.decorators import api_view

from note.models import Note
from note.serializers import NoteSerializer

# Create your views here.
def index(request):
    return HttpResponse("Note view.")

#
# API
#

# i.e. python3 manage.py runserver 0:8080
# i.e. http://localhost:8080/note/api/note

@api_view(['GET', 'POST'])
def noteListCreate(request):
    if request.method == 'GET':
        notes = Note.objects.all()
        
        id = request.query_params.get('id', None)
        if id is not None:
            notes = notes.filter(id__icontains=id)
        
        note_serializer = NoteSerializer(notes, many=True)
        return JsonResponse(note_serializer.data, safe=False)
        # 'safe=False' for objects serialization
 
    elif request.method == 'POST':
        note_data = JSONParser().parse(request)
        note_serializer = NoteSerializer(data=note_data)
        if note_serializer.is_valid():
            note_serializer.save()
            return JsonResponse(note_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(note_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
