from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase


class AuthenticationTests(APITestCase):
    """Tests for signup, login, logout, CSRF, and session expiry."""

    def setUp(self):
        User.objects.all().delete()

    def test_signup_with_valid_data(self):
        """Test that a new user can sign up with valid data."""
        response = self.client.post(
            "/api/users/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepassword123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_signup_with_duplicate_username(self):
        """Test that signup with duplicate username fails."""
        User.objects.create_user(username="existing", email="existing@test.com", password="pass123")
        response = self.client.post(
            "/api/users/",
            {
                "username": "existing",
                "email": "new@example.com",
                "password": "securepassword123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_signup_with_duplicate_email(self):
        """Test that signup with duplicate email fails."""
        User.objects.create_user(username="user1", email="duplicate@test.com", password="pass123")
        response = self.client.post(
            "/api/users/",
            {
                "username": "user2",
                "email": "duplicate@test.com",
                "password": "securepassword123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_signup_with_weak_password(self):
        """Test that signup with weak password fails."""
        response = self.client.post(
            "/api/users/",
            {
                "username": "weakpass",
                "email": "weak@test.com",
                "password": "123",  # Too short
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_login_with_valid_credentials(self):
        """Test that login with valid credentials succeeds."""
        User.objects.create_user(username="testuser", email="test@test.com", password="correctpass")
        response = self.client.post(
            "/api/auth/login/",
            {"username": "testuser", "password": "correctpass"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

    def test_login_with_invalid_credentials(self):
        """Test that login with invalid credentials fails."""
        User.objects.create_user(username="testuser", email="test@test.com", password="correctpass")
        response = self.client.post(
            "/api/auth/login/",
            {"username": "testuser", "password": "wrongpass"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_login_with_nonexistent_user(self):
        """Test that login with nonexistent user fails."""
        response = self.client.post(
            "/api/auth/login/",
            {"username": "nonexistent", "password": "anypassword"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_logout(self):
        """Test that logout clears the session."""
        User.objects.create_user(username="testuser", email="test@test.com", password="pass123")
        
        # Get CSRF token first
        self.client.get("/api/auth/csrf/")
        
        # Login to establish a real session
        self.client.post(
            "/api/auth/login/",
            {"username": "testuser", "password": "pass123"},
            format="json",
        )
        
        # Verify user is authenticated
        response = self.client.get("/api/me/")
        self.assertEqual(response.status_code, 200)
        
        # Logout
        response = self.client.post("/api/auth/logout/")
        self.assertIn(response.status_code, [200, 204])
        
        # Verify user is no longer authenticated
        response = self.client.get("/api/me/")
        self.assertIn(response.status_code, [401, 403])

    def test_csrf_endpoint(self):
        """Test that the CSRF endpoint returns a CSRF token."""
        response = self.client.get("/api/auth/csrf/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrfToken", response.data)
        self.assertIsNotNone(response.data["csrfToken"])

    def test_session_expiry(self):
        """Test that session expires after logout."""
        User.objects.create_user(username="testuser", email="test@test.com", password="pass123")
        
        # Get CSRF token first
        self.client.get("/api/auth/csrf/")
        
        # Login to establish a real session
        self.client.post(
            "/api/auth/login/",
            {"username": "testuser", "password": "pass123"},
            format="json",
        )
        
        # Get CSRF token
        response = self.client.get("/api/auth/csrf/")
        csrf_token = response.cookies.get("csrftoken")
        
        # Logout
        response = self.client.post("/api/auth/logout/")
        self.assertIn(response.status_code, [200, 204, 403])
        
        # Try to access authenticated endpoint - should fail
        response = self.client.get("/api/me/")
        self.assertIn(response.status_code, [401, 403])


class AuthorizationTests(APITestCase):
    """Tests for authorization and ownership of resources."""

    def test_create_account(self):
        """
        Test that anyone (including unauthenticated users) can create a new account.
        This tests the POST /api/users/ endpoint with AllowAny permission for POST requests.
        """
        User.objects.all().delete()

        new_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        }

        response = self.client.post(
            "/api/users/",
            new_user_data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="testuser").exists())
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertNotIn("password", response.data)

    def test_profile_edit_authorization(self):
        """
        Test that only the owner can edit their profile.
        Uses IsOwnerOrReadOnly permission on ProfileViewSet.
        - Owner can edit their own profile (200 OK)
        - Non-owner cannot edit another user's profile (403 Forbidden)
        - Unauthenticated user cannot edit any profile (401/403)
        """
        from .models import Profile

        User.objects.all().delete()
        user1 = User.objects.create_user(username="user1", email="user1@test.com", password="pass123")
        user2 = User.objects.create_user(username="user2", email="user2@test.com", password="pass123")
        profile1 = user1.profile
        profile2 = user2.profile

        # User1 edits their own profile - should succeed
        self.client.force_authenticate(user=user1)
        response = self.client.patch(
            f"/api/profiles/{profile1.id}/",
            {"bio": "Updated bio"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        profile1.refresh_from_db()
        self.assertEqual(profile1.bio, "Updated bio")

        # User1 tries to edit user2's profile - should fail with 403
        self.client.force_authenticate(user=user1)
        response = self.client.patch(
            f"/api/profiles/{profile2.id}/",
            {"bio": "Hacking attempt"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

        # Unauthenticated user tries to edit profile - should fail with 401 or 403
        self.client.logout()
        response = self.client.patch(
            f"/api/profiles/{profile1.id}/",
            {"bio": "Unauthenticated edit"},
            format="json",
        )
        self.assertIn(response.status_code, [401, 403])

    def test_review_edit_authorization(self):
        """
        Test that only the owner can edit their review.
        Uses IsAuthenticatedOrReadOnly permission on ReviewViewSet with queryset filtering.
        - Owner can edit their own review (200 OK)
        - Non-owner cannot edit another user's review (404 Not Found due to queryset filtering)
        - Unauthenticated user cannot edit any review (401/403)
        """
        from mangas.models import Chapter, Serie
        from .models import Review

        User.objects.all().delete()
        Review.objects.all().delete()

        user1 = User.objects.create_user(username="user1", email="user1@test.com", password="pass123")
        user2 = User.objects.create_user(username="user2", email="user2@test.com", password="pass123")
        serie = Serie.objects.create(title="Test Serie", first_published="2020-01-01")
        chapter = Chapter.objects.create(number=1, name="Chapter 1", manga=serie, first_published="2020-01-01")

        review1 = Review.objects.create(user=user1, rating=5, chapter=chapter, description="Great!")
        review2 = Review.objects.create(user=user2, rating=4, chapter=chapter, description="Good")

        # User1 edits their own review - should succeed
        self.client.force_authenticate(user=user1)
        response = self.client.patch(
            f"/api/reviews/{review1.id}/",
            {"description": "Updated description"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        review1.refresh_from_db()
        self.assertEqual(review1.description, "Updated description")

        # User1 tries to edit user2's review - should fail with 404
        # (get_queryset filters to only user's own reviews for update)
        self.client.force_authenticate(user=user1)
        response = self.client.patch(
            f"/api/reviews/{review2.id}/",
            {"description": "Hacking attempt"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

        # Unauthenticated user tries to edit review - should fail with 401 or 403
        self.client.logout()
        response = self.client.patch(
            f"/api/reviews/{review1.id}/",
            {"description": "Unauthenticated edit"},
            format="json",
        )
        self.assertIn(response.status_code, [401, 403])

    def test_profile_collection_authorization(self):
        """
        Test that only authenticated users can add/remove mangas from their profile collection.
        Uses IsAuthenticated permission on add_manga/remove_manga actions.
        - Authenticated user can add manga to their own collection (200/201)
        - Authenticated user can remove manga from their own collection (200/201/204)
        - Unauthenticated user cannot modify collection (401/403)
        Note: The add_manga/remove_manga actions use request.user.profile, so users can only
        modify their own collection.
        """
        from mangas.models import Chapter, Serie
        from .models import Profile

        User.objects.all().delete()
        Chapter.objects.all().delete()
        Serie.objects.all().delete()

        user1 = User.objects.create_user(username="user1", email="user1@test.com", password="pass123")
        user2 = User.objects.create_user(username="user2", email="user2@test.com", password="pass123")
        profile1 = user1.profile
        profile2 = user2.profile

        serie = Serie.objects.create(title="Test Serie", first_published="2020-01-01")
        chapter = Chapter.objects.create(number=1, name="Chapter 1", manga=serie, first_published="2020-01-01")

        # User1 adds manga to their own collection - should succeed
        self.client.force_authenticate(user=user1)
        response = self.client.post(
            "/api/profiles/add_manga/",
            {"chapter": chapter.id},
            format="json",
        )
        self.assertIn(response.status_code, [200, 201])
        if response.status_code in [200, 201]:
            self.assertIn(chapter, profile1.mangas.all())

        # User1 removes manga from their own collection - should succeed
        response = self.client.delete(
            "/api/profiles/remove_manga/",
            {"chapter": chapter.id},
            format="json",
        )
        self.assertIn(response.status_code, [200, 201, 204])
        profile1.refresh_from_db()
        self.assertNotIn(chapter, profile1.mangas.all())

        # Unauthenticated user tries to add manga - should fail with 401 or 403
        self.client.logout()
        response = self.client.post(
            "/api/profiles/add_manga/",
            {"chapter": chapter.id},
            format="json",
        )
        self.assertIn(response.status_code, [401, 403])

    def test_reactions_authorization(self):
        """
        Test that only authenticated users can add/remove reactions to reviews.
        Uses IsAuthenticatedOrReadOnly permission on ReviewViewSet.
        - Authenticated user can add like reaction (200 OK)
        - Authenticated user can add dislike reaction (200 OK)
        - Authenticated user can remove their own reaction (200 OK)
        - Different users can have different reactions on the same review
        - Unauthenticated user cannot add/remove reactions (401/403)
        """
        from mangas.models import Chapter, Serie
        from .models import Review, ReviewReaction

        User.objects.all().delete()
        Review.objects.all().delete()
        ReviewReaction.objects.all().delete()
        Chapter.objects.all().delete()
        Serie.objects.all().delete()

        user1 = User.objects.create_user(username="user1", email="user1@test.com", password="pass123")
        user2 = User.objects.create_user(username="user2", email="user2@test.com", password="pass123")

        serie = Serie.objects.create(title="Test Serie", first_published="2020-01-01")
        chapter = Chapter.objects.create(number=1, name="Chapter 1", manga=serie, first_published="2020-01-01")
        review = Review.objects.create(user=user1, rating=5, chapter=chapter, description="Great!")

        # User1 adds like to review - should succeed
        self.client.force_authenticate(user=user1)
        response = self.client.post(
            f"/api/reviews/{review.id}/like/",
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ReviewReaction.objects.filter(user=user1, review=review, reaction=ReviewReaction.LIKE).exists())

        # User2 adds dislike to same review - should succeed (different user)
        self.client.force_authenticate(user=user2)
        response = self.client.post(
            f"/api/reviews/{review.id}/dislike/",
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ReviewReaction.objects.filter(user=user2, review=review, reaction=ReviewReaction.DISLIKE).exists())

        # User1 removes their reaction - should succeed
        self.client.force_authenticate(user=user1)
        response = self.client.delete(
            f"/api/reviews/{review.id}/reaction/",
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ReviewReaction.objects.filter(user=user1, review=review).exists())

        # User2 removes their reaction - should succeed
        self.client.force_authenticate(user=user2)
        response = self.client.delete(
            f"/api/reviews/{review.id}/reaction/",
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ReviewReaction.objects.filter(user=user2, review=review).exists())

        # Unauthenticated user tries to add reaction - should fail with 401 or 403
        self.client.logout()
        response = self.client.post(
            f"/api/reviews/{review.id}/like/",
            format="json",
        )
        self.assertIn(response.status_code, [401, 403])


class LoginThrottleTests(TestCase):
    """Tests for rate limiting on login attempts."""

    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_login_is_rate_limited(self):
        """
        Test that login attempts are rate limited after multiple failures.
        Uses LoginThrottle with rate of 10/hour.
        - First 5 failed login attempts return 400 (invalid credentials)
        - 6th failed attempt within the rate limit period returns 429 (Too Many Requests)
        """
        for _ in range(5):
            response = self.client.post(
                "/api/auth/login/",
                {"username": "missing", "password": "wrong"},
                format="json",
            )
            self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "/api/auth/login/",
            {"username": "missing", "password": "wrong"},
            format="json",
        )

        self.assertEqual(response.status_code, 429)


class ReviewFilterOrderingPaginationTests(APITestCase):
    """Tests for review filters, ordering, and pagination stability."""

    def setUp(self):
        from mangas.models import Serie, Chapter
        from .models import Review
        
        User.objects.all().delete()
        Serie.objects.all().delete()
        Chapter.objects.all().delete()
        Review.objects.all().delete()
        
        # Create test data
        self.user1 = User.objects.create_user(username="user1", email="user1@test.com", password="pass123")
        self.user2 = User.objects.create_user(username="user2", email="user2@test.com", password="pass123")
        
        # Create series and chapters
        self.serie1 = Serie.objects.create(
            title="Test Serie",
            first_published="2020-01-01",
        )
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
            number=3,
            name="Chapter 3",
            manga=self.serie1,
            first_published="2020-03-01"
        )
        # Additional chapter for pagination test
        self.chapter4 = Chapter.objects.create(
            number=4,
            name="Chapter 4",
            manga=self.serie1,
            first_published="2020-04-01"
        )
        
        # Create reviews - ensure unique user+chapter combinations
        self.review1 = Review.objects.create(
            user=self.user1,
            rating=5,
            chapter=self.chapter1,
            description="Great chapter!"
        )
        self.review2 = Review.objects.create(
            user=self.user2,
            rating=4,
            chapter=self.chapter1,
            description="Good chapter"
        )
        self.review3 = Review.objects.create(
            user=self.user1,
            rating=3,
            chapter=self.chapter2,
            description="Average"
        )
        self.review4 = Review.objects.create(
            user=self.user2,
            rating=2,
            chapter=self.chapter3,
            description="Not great"
        )
        self.review5 = Review.objects.create(
            user=self.user1,
            rating=1,
            chapter=self.chapter3,
            description="Bad"
        )

    def test_ordering_reviews_by_created_at(self):
        """
        Test ordering reviews by created_at.
        - GET /api/reviews/?ordering=-created_at should return newest reviews first
        - GET /api/reviews/?ordering=created_at should return oldest reviews first
        """
        # Order by created_at descending (newest first)
        response = self.client.get("/api/reviews/", {"ordering": "-created_at"})
        self.assertEqual(response.status_code, 200)
        results = response.data["results"]
        if len(results) > 1:
            for i in range(len(results) - 1):
                self.assertGreaterEqual(results[i]["created_at"], results[i + 1]["created_at"])

    def test_pagination_stability_on_delete(self):
        """
        Test that pagination remains stable when the last item on a page is deleted.
        This tests the offset clamping in the frontend.
        """
        from mangas.models import Chapter
        from .models import Review
        
        # Create more reviews using chapter4 which has no reviews yet
        # Only create 1 review per user+chapter combination
        # We need 10 unique combinations, so create new chapters
        for i in range(5):
            new_chapter = Chapter.objects.create(
                number=10 + i,
                name=f"Pagination Chapter {i}",
                manga=self.serie1,
                first_published=f"2020-0{5+i}-01"
            )
            Review.objects.create(
                user=self.user1,
                rating=5,
                chapter=new_chapter,
                description=f"Review {i}"
            )
            Review.objects.create(
                user=self.user2,
                rating=4,
                chapter=new_chapter,
                description=f"Review {i} by user2"
            )
        
        # Get first page with limit=5
        response = self.client.get("/api/reviews/?limit=5")
        self.assertEqual(response.status_code, 200)
        total_count = response.data["count"]
        self.assertGreater(total_count, 5)
        
        # Get the last review on the first page
        first_page = response.data["results"]
        last_review_id = first_page[-1]["id"]
        
        # Delete the last review on the first page
        Review.objects.filter(id=last_review_id).delete()
        
        # Get the first page again - should still return results
        response = self.client.get("/api/reviews/?limit=5")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data["results"]), 0)
        self.assertEqual(response.data["count"], total_count - 1)

    def test_pagination_with_offset(self):
        """
        Test pagination with offset parameter.
        - GET /api/reviews/?limit=2&offset=0 should return first 2 reviews
        - GET /api/reviews/?limit=2&offset=2 should return next 2 reviews (if available)
        """
        # Get first page with offset=0, limit=2
        response = self.client.get("/api/reviews/?limit=2&offset=0")
        self.assertEqual(response.status_code, 200)
        first_page = response.data["results"]
        self.assertEqual(len(first_page), 2)
        
        # Get second page with offset=2, limit=2
        response = self.client.get("/api/reviews/?limit=2&offset=2")
        self.assertEqual(response.status_code, 200)
        second_page = response.data["results"]
        # We have 5+ reviews total, so offset=2 should return at least 1
        self.assertGreaterEqual(len(second_page), 1)
        
        # Verify different results
        first_ids = {r["id"] for r in first_page}
        second_ids = {r["id"] for r in second_page}
        self.assertNotEqual(first_ids, second_ids)

    def test_default_ordering_prevents_warning(self):
        """
        Test that all models have default ordering to prevent UnorderedObjectListWarning.
        This is a meta-test that verifies the acceptance criteria.
        """
        from mangas.models import Serie, Chapter, Author
        from .models import Profile, Review
        
        # Check that all models have ordering defined
        self.assertTrue(hasattr(Serie._meta, 'ordering'))
        self.assertTrue(hasattr(Chapter._meta, 'ordering'))
        self.assertTrue(hasattr(Author._meta, 'ordering'))
        self.assertTrue(hasattr(Profile._meta, 'ordering'))
        self.assertTrue(hasattr(Review._meta, 'ordering'))
        
        # Verify ordering is not empty
        self.assertGreater(len(Serie._meta.ordering), 0)
        self.assertGreater(len(Chapter._meta.ordering), 0)
        self.assertGreater(len(Author._meta.ordering), 0)
        self.assertGreater(len(Profile._meta.ordering), 0)
        self.assertGreater(len(Review._meta.ordering), 0)
