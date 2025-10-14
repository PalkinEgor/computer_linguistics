from django.urls import path
from django.conf.urls import url
from db.views import CorpusAPIView, TextAPIView

from db.views import (
    getTest,
    postTest,
    deleteTest
)

urlpatterns = [
    path('getTest',getTest , name='getTest'),
    path('postTest',postTest , name='postTest'),
    path('deleteTest',deleteTest , name='deleteTest'),

    path('api/corpus/', CorpusAPIView.as_view()),
    path('api/corpus/<int:corpus_id>/', CorpusAPIView.as_view()),

    path('api/text/', TextAPIView.as_view()),
    path('api/text/<int:text_id>/', TextAPIView.as_view()),
]