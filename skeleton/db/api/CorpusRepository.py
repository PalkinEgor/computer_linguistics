from db.models import Corpus, Text

class CorpusRepository:
    def get_all(self):
        return Corpus.objects.all()

    def get(self, corpus_id):
        return Corpus.objects.prefetch_related('texts').get(id=corpus_id)

    def create(self, data):
        return Corpus.objects.create(**data)

    def update(self, corpus_id, data):
        corpus = Corpus.objects.get(id=corpus_id)
        for key, value in data.items():
            setattr(corpus, key, value)
        corpus.save()
        return corpus

    def delete(self, corpus_id):
        Corpus.objects.get(id=corpus_id).delete()