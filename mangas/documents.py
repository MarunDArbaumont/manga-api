from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Serie, Chapter, Author

@registry.register_document
class MnagaDocument(Document):
    author = fields.TextField(attr="author.name")

    class Index:
        name = "manga"

    class Django:
        model = Serie
        fields = ["title", "genre", "first_published"]


@registry.register_document
class ChapterDocument(Document):
    manga_title = fields.TextField(attr="manga.title")

    class Index:
        name = "chapter"

    class Django:
        model = Chapter
        fields = ["name", "number", "first_published"]