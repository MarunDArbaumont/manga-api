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


class FilterOrderingTests(APITestCase):
    """Tests for manga/series filters and ordering."""

    def setUp(self):
        from django.contrib.auth.models import User
        
        User.objects.all().delete()
        Author.objects.all().delete()
        Serie.objects.all().delete()
        Chapter.objects.all().delete()
        
        # Create test data
        self.user1 = User.objects.create_user(username="user1", email="user1@test.com", password="pass123")
        
        # Create authors
        self.author1 = Author.objects.create(
            name="Author A",
            birth_day="2000-01-01",
        )
        self.author2 = Author.objects.create(
            name="Author B",
            birth_day="2000-02-01",
        )
        
        # Create series with different properties
        self.serie1 = Serie.objects.create(
            title="Ongoing Serie",
            first_published="2020-01-01",
            last_published=None,  # Not finished
            genre="shonen"
        )
        self.serie2 = Serie.objects.create(
            title="Finished Serie",
            first_published="2019-01-01",
            last_published="2020-01-01",  # Finished
            genre="seinen"
        )
        self.serie3 = Serie.objects.create(
            title="Another Ongoing",
            first_published="2021-01-01",
            last_published=None,
            genre="shonen"
        )
        
        # Add authors to series
        self.serie1.authors.add(self.author1)
        self.serie2.authors.add(self.author2)
        self.serie3.authors.add(self.author1, self.author2)
        
        # Create chapters
        self.chapter1 = Chapter.objects.create(
            number=1,
            name="Chapter 1",
            manga=self.serie1,
            first_published="2020-01-01"
        )
        self.chapter2 = Chapter.objects.create(
            number=2,
            name="Chapter 2",
            manga=self.serie1,
            first_published="2020-02-01"
        )
        self.chapter3 = Chapter.objects.create(
            number=1,
            name="Chapter 1",
            manga=self.serie2,
            first_published="2019-01-01"
        )

    def test_filter_series_by_ongoing(self):
        """
        Test filtering series by ongoing status.
        - GET /api/series/?ongoing=true should return only series without last_published
        - GET /api/series/?ongoing=false should return only series with last_published
        """
        # Filter for ongoing series
        response = self.client.get("/api/series/?ongoing=true")
        self.assertEqual(response.status_code, 200)
        ongoing_series = response.data["results"]
        self.assertEqual(len(ongoing_series), 2)  # serie1 and serie3
        
        # Verify all returned series are ongoing
        for serie in ongoing_series:
            self.assertIsNone(serie["last_published"])

    def test_filter_series_by_genre(self):
        """
        Test filtering series by genre.
        - GET /api/series/?genre=shonen should return only shonen series
        - GET /api/series/?genre=seinen should return only seinen series
        """
        # Filter for shonen series
        response = self.client.get("/api/series/?genre=shonen")
        self.assertEqual(response.status_code, 200)
        shonen_series = response.data["results"]
        self.assertEqual(len(shonen_series), 2)  # serie1 and serie3
        
        for serie in shonen_series:
            self.assertEqual(serie["genre"], "shonen")

    def test_filter_series_by_title(self):
        """
        Test filtering series by title (exact match).
        - GET /api/series/?title=Ongoing Serie should return the series with that exact title
        """
        # Filter for series with exact title match
        response = self.client.get("/api/series/?title=Ongoing Serie")
        self.assertEqual(response.status_code, 200)
        matching_series = response.data["results"]
        self.assertGreater(len(matching_series), 0)
        
        for serie in matching_series:
            self.assertEqual(serie["title"], "Ongoing Serie")

    def test_ordering_series_by_title(self):
        """
        Test ordering series by title.
        - GET /api/series/?ordering=title should return series ordered alphabetically by title
        - GET /api/series/?ordering=-title should return series in reverse alphabetical order
        """
        # Order by title ascending
        response = self.client.get("/api/series/", {"ordering": "title"})
        self.assertEqual(response.status_code, 200)
        titles_asc = [s["title"] for s in response.data["results"]]
        self.assertEqual(titles_asc, sorted(titles_asc))
        
        # Order by title descending
        response = self.client.get("/api/series/", {"ordering": "-title"})
        self.assertEqual(response.status_code, 200)
        titles_desc = [s["title"] for s in response.data["results"]]
        self.assertEqual(titles_desc, sorted(titles_desc, reverse=True))

    def test_ordering_chapters_by_number(self):
        """
        Test ordering chapters by number within a series.
        - GET /api/chapters/?manga=<id>&ordering=number should return chapters in ascending order
        """
        # Order chapters by number
        response = self.client.get(f"/api/chapters/", {"manga": self.serie1.id, "ordering": "number"})
        self.assertEqual(response.status_code, 200)
        chapters = response.data["results"]
        numbers = [c["number"] for c in chapters]
        self.assertEqual(numbers, sorted(numbers))

    def test_chapter_uniqueness_constraint(self):
        """
        Test that chapter numbers are unique per manga.
        - Creating a duplicate chapter number for the same manga should fail
        """
        from django.db.utils import IntegrityError
        
        # Try to create a duplicate chapter number for serie1
        with self.assertRaises(IntegrityError):
            Chapter.objects.create(
                number=1,  # Duplicate of chapter1
                name="Duplicate Chapter",
                manga=self.serie1,
                first_published="2020-03-01"
            )
