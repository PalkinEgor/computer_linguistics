from rest_framework import serializers
from db.models import Corpus, Text

class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = ['id', 'title', 'description', 'text', 'corpus', 'has_translation']

class CorpusSerializer(serializers.ModelSerializer):
    texts = TextSerializer(many=True, read_only=True)

    class Meta:
        model = Corpus
        fields = ['id', 'name', 'description', 'genre', 'texts']