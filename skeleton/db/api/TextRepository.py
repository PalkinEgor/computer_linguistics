from db.models import Text

class TextRepository:
    def get_all(self):
        return Text.objects.all()

    def get(self, text_id):
        return Text.objects.get(id=text_id)

    def create(self, data):
        return Text.objects.create(**data)

    def update(self, text_id, data):
        text = Text.objects.get(id=text_id)
        for key, value in data.items():
            setattr(text, key, value)
        text.save()
        return text

    def delete(self, text_id):
        Text.objects.get(id=text_id).delete()