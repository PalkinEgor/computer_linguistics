from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponseRedirect, HttpResponse
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from django.db.models import Q
from django.conf import settings
from.onthology_namespace import *
from .models import Test
from core.settings import *

# API IMPORTS
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework import status

# REPO IMPORTS
from db.api.TestRepository import TestRepository
from db.api.CorpusRepository import CorpusRepository
from db.api.TextRepository import TextRepository
from db.api.OntologyRepository import OntologyRepository
from db.serializers import CorpusSerializer, TextSerializer

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getTest(request):
    id = request.GET.get('id', None)
    if id is None:
        return HttpResponse(status=400)
    
    testRepo = TestRepository()
    result = testRepo.getTest(id = id)
    return Response(result)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def postTest(request):
    data = json.loads(request.body.decode('utf-8'))
    testRepo = TestRepository()
    test = testRepo.postTest(test_data = data)
    return JsonResponse(test)

@api_view(['DELETE', ])
@permission_classes((AllowAny,))
def deleteTest(request):
    id = request.GET.get('id', None)
    if id is None:
        return HttpResponse(status=400)
    
    testRepo = TestRepository()
    result = testRepo.deleteTest(id = id)
    return Response(result)

class CorpusAPIView(APIView):
    repo = CorpusRepository()

    def get(self, request, corpus_id=None):
        if corpus_id:
            corpus = self.repo.get(corpus_id)
            serializer = CorpusSerializer(corpus)
        else:
            corpuses = self.repo.get_all()
            serializer = CorpusSerializer(corpuses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CorpusSerializer(data=request.data)
        if serializer.is_valid():
            corpus = self.repo.create(serializer.validated_data)
            return Response(CorpusSerializer(corpus).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, corpus_id):
        serializer = CorpusSerializer(data=request.data)
        if serializer.is_valid():
            corpus = self.repo.update(corpus_id, serializer.validated_data)
            return Response(CorpusSerializer(corpus).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, corpus_id):
        self.repo.delete(corpus_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class TextAPIView(APIView):
    repo = TextRepository()

    def get(self, request, text_id=None):
        if text_id:
            text = self.repo.get(text_id)
            serializer = TextSerializer(text)
        else:
            texts = self.repo.get_all()
            serializer = TextSerializer(texts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TextSerializer(data=request.data)
        if serializer.is_valid():
            text = self.repo.create(serializer.validated_data)
            return Response(TextSerializer(text).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, text_id):
        serializer = TextSerializer(data=request.data)
        if serializer.is_valid():
            text = self.repo.update(text_id, serializer.validated_data)
            return Response(TextSerializer(text).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, text_id):
        self.repo.delete(text_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
def make_repo():
    return OntologyRepository(
        uri=getattr(settings, "NEO4J_URI", None),
        user=getattr(settings, "NEO4J_USER", None),
        password=getattr(settings, "NEO4J_PASSWORD", None)
    )

class OntologyListAPIView(APIView):
    def get(self, request):
        repo = make_repo()
        try:
            data = repo.get_ontology()
            return Response(data)
        finally:
            repo.close()

class ClassCreateAPIView(APIView):
    def post(self, request):
        title = request.data.get('title')
        description = request.data.get('description', '')
        parent_uri = request.data.get('parent_uri', None)
        if not title:
            return Response({"error": "title is required"}, status=status.HTTP_400_BAD_REQUEST)
        repo = make_repo()
        try:
            node = repo.create_class(title, description, parent_uri)
            return Response(node, status=status.HTTP_201_CREATED)
        finally:
            repo.close()

class ClassDetailAPIView(APIView):
    def get(self, request, uri):
        repo = make_repo()
        try:
            node = repo.get_class(uri)
            if not node:
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(node)
        finally:
            repo.close()

    def put(self, request, uri):
        title = request.data.get('title')
        description = request.data.get('description')
        repo = make_repo()
        try:
            node = repo.update_class(uri, title=title, description=description)
            if not node:
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(node)
        finally:
            repo.close()

    def delete(self, request, uri):
        repo = make_repo()
        try:
            repo.delete_class(uri)
            return Response(status=status.HTTP_204_NO_CONTENT)
        finally:
            repo.close()
    
