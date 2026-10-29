from django.contrib.auth.models import User
from django.db.models import Value
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Author, Chapter, Serie
from .serializers import (
    AuthorSerializer,
    ChapterSerializer,
    ChapterWriteSerializer,
    SingleSerieSerializer,
)


class CatalogAPITests(APITestCase):
    def setUp(self):
        self.author = Author.objects.create(
            name="Eiichiro Oda",
            birth_day=timezone.now(),
        )
        self.serie = Serie.objects.create(
            title="One Piece",
            first_published=timezone.now(),
            description="A pirate adventure.",
        )
        self.serie.authors.add(self.author)
        self.chapter = Chapter.objects.create(
            number=1,
            name="Romance Dawn",
            manga=self.serie,
            first_published=timezone.now(),
        )
        self.reader = User.objects.create_user(
            username="reader",
            password="test-password-123",
        )
        self.staff = User.objects.create_user(
            username="admin",
            password="test-password-123",
            is_staff=True,
        )
        self.chapter_payload = {
            "number": 2,
            "name": "They Call Him Straw Hat Luffy",
            "manga": self.serie.pk,
            "first_published": timezone.now().isoformat(),
        }

    def test_anonymous_can_read_chapters(self):
        response = self.client.get("/api/chapters/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["average_rating"], None)
        self.assertEqual(response.data["results"][0]["count_rating"], 0)

    def test_reader_cannot_create_chapter(self):
        self.client.force_authenticate(self.reader)

        response = self.client.post(
            "/api/chapters/",
            self.chapter_payload,
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_staff_can_create_chapter(self):
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            "/api/chapters/",
            self.chapter_payload,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["manga"], self.serie.pk)
        self.assertTrue(
            Chapter.objects.filter(
                manga=self.serie,
                number=self.chapter_payload["number"],
            ).exists()
        )

    def test_reader_cannot_create_serie_or_author(self):
        self.client.force_authenticate(self.reader)

        serie_response = self.client.post(
            "/api/series/",
            {
                "title": "Bleach",
                "first_published": timezone.now().isoformat(),
                "description": "Soul reapers.",
                "authors": [self.author.pk],
            },
            format="json",
        )
        author_response = self.client.post(
            "/api/authors/",
            {
                "name": "Tite Kubo",
                "birth_day": timezone.now().isoformat(),
            },
            format="json",
        )

        self.assertEqual(serie_response.status_code, 403)
        self.assertEqual(author_response.status_code, 403)

    def test_staff_can_create_serie(self):
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            "/api/series/",
            {
                "title": "Bleach",
                "first_published": timezone.now().isoformat(),
                "description": "Soul reapers.",
                "authors": [self.author.pk],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "Bleach")

    def test_author_response_includes_series(self):
        response = self.client.get("/api/authors/")

        self.assertEqual(response.status_code, 200)
        author_data = response.data["results"][0]
        self.assertIn("series", author_data)
        self.assertEqual(author_data["series"][0]["title"], "One Piece")

    def test_serie_detail_includes_aggregate_fields(self):
        response = self.client.get(f"/api/series/{self.serie.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("average_rating", response.data)
        self.assertIn("count_rating", response.data)
        self.assertEqual(response.data["count_rating"], 0)
        self.assertEqual(response.data["chapters"][0]["count_rating"], 0)

    def test_chapter_write_serializer_requires_manga(self):
        serializer = ChapterWriteSerializer(
            data={
                "number": 2,
                "name": "Missing Manga",
                "first_published": timezone.now().isoformat(),
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("manga", serializer.errors)

    def test_read_serializers_expose_expected_fields(self):
        self.chapter.average_rating = 4.5
        self.chapter.count_rating = 2

        chapter_data = ChapterSerializer(self.chapter).data
        serie_data = SingleSerieSerializer(
            Serie.objects.annotate(
                average_rating=Value(4.5),
                count_rating=Value(2),
            ).get(pk=self.serie.pk)
        ).data
        author_data = AuthorSerializer(self.author).data

        self.assertEqual(chapter_data["average_rating"], 4.5)
        self.assertEqual(chapter_data["count_rating"], 2)
        self.assertEqual(serie_data["average_rating"], 4.5)
        self.assertEqual(serie_data["count_rating"], 2)
        self.assertIn("series", author_data)


class ChapterSerializerTests(TestCase):
    def test_read_serializer_keeps_manga_read_only(self):
        self.assertTrue(ChapterSerializer().fields["manga"].read_only)
        self.assertFalse(ChapterWriteSerializer().fields["manga"].read_only)
