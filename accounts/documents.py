from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Review, Profile
from mangas.models import Chapter, Serie


@registry.register_document
class ReviewDocument(Document):
    """Elasticsearch document for Review model."""
    description = fields.TextField(
        attr='description',
        fields={
            'raw': fields.KeywordField(),
        }
    )
    rating = fields.IntegerField(attr='rating')
    is_edited = fields.BooleanField(attr='is_edited')
    created_at = fields.DateField(attr='created_at')
    
    # ForeignKey - user
    user = fields.ObjectField(
        properties={
            'id': fields.IntegerField(),
            'username': fields.KeywordField(),
        }
    )
    
    # ForeignKey - chapter
    chapter = fields.ObjectField(
        properties={
            'id': fields.IntegerField(),
            'number': fields.FloatField(),
            'name': fields.TextField(),
            'manga': fields.ObjectField(
                properties={
                    'id': fields.IntegerField(),
                    'title': fields.TextField(),
                }
            ),
        }
    )
    
    # For nested comments (parent-child relationships)
    parent = fields.IntegerField(attr='parent_id')

    class Index:
        name = 'reviews'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Review
        fields = ['id']
        
        def get_queryset(self):
            return Review.objects.select_related(
                'user',
                'chapter__manga'
            ).prefetch_related(
                'comments'
            )
        
        def get_instances_from_related(self, related_instance):
            if isinstance(related_instance, Chapter):
                return related_instance.review_set.filter(parent__isnull=True)


@registry.register_document
class ProfileDocument(Document):
    """Elasticsearch document for Profile model."""
    bio = fields.TextField(attr='bio')
    
    # OneToOne - user
    user = fields.ObjectField(
        properties={
            'id': fields.IntegerField(),
            'username': fields.KeywordField(),
        }
    )
    
    # ManyToMany - mangas (chapters in collection)
    mangas = fields.ObjectField(
        properties={
            'id': fields.IntegerField(),
            'number': fields.FloatField(),
            'name': fields.TextField(),
            'manga': fields.ObjectField(
                properties={
                    'id': fields.IntegerField(),
                    'title': fields.TextField(),
                }
            ),
        },
        multi=True
    )

    class Index:
        name = 'profiles'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Profile
        fields = ['id']
        
        def get_queryset(self):
            return Profile.objects.prefetch_related(
                'mangas__manga'
            )
