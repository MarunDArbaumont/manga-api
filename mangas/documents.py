from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Serie, Author, Chapter


@registry.register_document
class SerieDocument(Document):
    """Elasticsearch document for Serie model."""
    title = fields.TextField(
        attr='title',
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField(),
        }
    )
    description = fields.TextField(attr='description')
    genre = fields.KeywordField(attr='genre')
    first_published = fields.DateField(attr='first_published')
    last_published = fields.DateField(attr='last_published')
    authors = fields.TextField(
        attr='authors_indexing',
        fields={
            'raw': fields.KeywordField(),
        }
    )
    
    # Annotated fields
    average_rating = fields.FloatField()
    count_rating = fields.IntegerField()

    class Index:
        name = 'series'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Serie
        fields = ['id']
        
        # Prefetch related data for indexing
        def get_queryset(self):
            from django.db.models import Avg, Count, Prefetch
            from .querysets import chapters_with_ratings
            return Serie.objects.annotate(
                average_rating=Avg('chapters__review__rating'),
                count_rating=Count('chapters__review__rating'),
            ).prefetch_related(
                Prefetch('authors', queryset=Author.objects.all()),
                Prefetch('chapters', queryset=chapters_with_ratings())
            )
        
        def get_instances_from_related(self, related_instance):
            if isinstance(related_instance, Author):
                return related_instance.mangas.all()
            elif isinstance(related_instance, Chapter):
                return Serie.objects.filter(chapters=related_instance)


@registry.register_document
class AuthorDocument(Document):
    """Elasticsearch document for Author model."""
    name = fields.TextField(
        attr='name',
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField(),
        }
    )
    birth_day = fields.DateField(attr='birth_day')
    death_date = fields.DateField(attr='death_date')
    
    # ManyToMany field - mangas (series)
    mangas = fields.TextField(attr='mangas__title') 

    class Index:
        name = 'authors'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Author
        fields = ['id']
        
        def get_queryset(self):
            return Author.objects.prefetch_related('mangas')


@registry.register_document
class ChapterDocument(Document):
    """Elasticsearch document for Chapter model."""
    number = fields.FloatField(attr='number')
    name = fields.TextField(
        attr='name',
        fields={
            'raw': fields.KeywordField(),
        }
    )
    
    manga = fields.TextField(attr='manga__title')
    
    first_published = fields.DateField(attr='first_published')
    
    # Annotated fields
    average_rating = fields.FloatField()
    count_rating = fields.IntegerField()

    class Index:
        name = 'chapters'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Chapter
        fields = ['id']
        
        def get_queryset(self):
            from .querysets import chapters_with_ratings
            return chapters_with_ratings()
