![Test badge](https://github.com/MarunDArbaumont/manga-api/actions/workflows/ci.yml/badge.svg)
# API of mangas
The API is connected to a database and provides comprehensive endpoints for managing manga data, users, reviews, and more.

## Base URL
All endpoints are prefixed with `/api/`

---

## 📚 Manga Data Endpoints

### Series

#### Get all series
- **URL**: `/api/series/`
- **Method**: `GET`
- **Description**: Gets all manga series with their content (description, cover, genre, authors)
- **Response**: List of series with annotated average rating and rating count

#### Get single series by ID
- **URL**: `/api/series/<id>/`
- **Method**: `GET`
- **Description**: Gets a specific series with all its chapters and authors
- **Response**: Single series object with prefetched chapters and authors

#### Create new series
- **URL**: `/api/series/`
- **Method**: `POST`
- **Permission**: Admin only
- **Description**: Create a new manga series
- **Request Body**: Series data (title, first_published, description, genre, authors)

---

### Authors

#### Get all authors
- **URL**: `/api/authors/`
- **Method**: `GET`
- **Description**: Gets all authors with their mangas
- **Response**: List of authors with prefetched related mangas

#### Get single author by ID
- **URL**: `/api/authors/<id>/`
- **Method**: `GET`
- **Description**: Gets a specific author with all their mangas
- **Response**: Single author object with prefetched mangas

#### Create new author
- **URL**: `/api/authors/`
- **Method**: `POST`
- **Permission**: Admin only
- **Description**: Create a new author
- **Request Body**: Author data (name, birth_day, death_date, image)

---

### Chapters

#### Get all chapters
- **URL**: `/api/chapters/`
- **Method**: `GET`
- **Description**: Gets all chapters with their ratings and reviews
- **Response**: List of chapters with annotated average rating

#### Get single chapter
- **URL**: `/api/chapters/<id>/`
- **Method**: `GET`
- **Description**: Gets a specific chapter with its reviews and ratings

#### Create new chapter
- **URL**: `/api/chapters/`
- **Method**: `POST`
- **Permission**: Admin only
- **Description**: Create a new chapter
- **Request Body**: Chapter data (number, name, manga, first_published)

#### Update chapter
- **URL**: `/api/chapters/<id>/`
- **Method**: `PUT` or `PATCH`
- **Permission**: Admin only
- **Description**: Update an existing chapter

#### Delete chapter
- **URL**: `/api/chapters/<id>/`
- **Method**: `DELETE`
- **Permission**: Admin only
- **Description**: Delete a chapter

---

## 👥 User & Authentication Endpoints

### Authentication

#### Get CSRF Token
- **URL**: `/api/auth/csrf/`
- **Method**: `GET`
- **Description**: Get CSRF token required for authenticated requests
- **Response**: `{"csrfToken": "..."}`

#### Login
- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Description**: Authenticate and login a user
- **Request Body**: `{"username": "...", "password": "..."}`
- **Response**: `{"id": ..., "username": "..."}`

#### Logout
- **URL**: `/api/auth/logout/`
- **Method**: `POST`
- **Permission**: Authenticated only
- **Description**: Logout the current user

#### Get current user
- **URL**: `/api/me/`
- **Method**: `GET`
- **Permission**: Authenticated only
- **Description**: Get information about the currently authenticated user
- **Response**: `{"id": ..., "username": "..."}`

---

### Users

#### Get all users
- **URL**: `/api/users/`
- **Method**: `GET`
- **Description**: Get list of all users
- **Response**: List of user objects

#### Get single user by ID
- **URL**: `/api/users/<id>/`
- **Method**: `GET`
- **Description**: Get a specific user's information

#### Create new user (Signup)
- **URL**: `/api/users/`
- **Method**: `POST`
- **Description**: Register a new user
- **Request Body**: User registration data

---

### Profiles

#### Get all profiles
- **URL**: `/api/profiles/`
- **Method**: `GET`
- **Description**: Get list of all user profiles

#### Get single profile by ID
- **URL**: `/api/profiles/<id>/`
- **Method**: `GET`
- **Description**: Get a specific user's profile

#### Get profile by user ID
- **URL**: `/api/users/<user_id>/profile/`
- **Method**: `GET`
- **Description**: Get the profile for a specific user
- **Response**: Profile with prefetched mangas collection

#### Update profile
- **URL**: `/api/profiles/<id>/`
- **Method**: `PUT` or `PATCH`
- **Permission**: Owner or admin only
- **Description**: Update profile information

#### Add manga to collection
- **URL**: `/api/profiles/add_manga/`
- **Method**: `POST`
- **Permission**: Authenticated only
- **Description**: Add a manga chapter to user's collection
- **Request Body**: `{"chapter": <chapter_id>}`
- **Response**: `{"message": "Added <chapter_name> to collection"}`

#### Remove manga from collection
- **URL**: `/api/profiles/remove_manga/`
- **Method**: `DELETE`
- **Permission**: Authenticated only
- **Description**: Remove a manga chapter from user's collection
- **Request Body**: `{"chapter": <chapter_id>}`
- **Response**: `{"message": "Removed <chapter_name> from collection"}`

---

## 💬 Review Endpoints

### Reviews

#### Get all reviews
- **URL**: `/api/reviews/`
- **Method**: `GET`
- **Description**: Get all reviews with annotations (chapter average rating, like/dislike counts)
- **Response**: List of reviews with user, chapter, and reaction information

#### Get single review
- **URL**: `/api/reviews/<id>/`
- **Method**: `GET`
- **Description**: Get a specific review with all its details

#### Create review
- **URL**: `/api/reviews/`
- **Method**: `POST`
- **Permission**: Authenticated only
- **Description**: Create a new review for a chapter
- **Request Body**: Review data (chapter, rating, description)
- **Note**: Users can only create one review per chapter

#### Update review
- **URL**: `/api/reviews/<id>/`
- **Method**: `PUT` or `PATCH`
- **Permission**: Owner or admin only
- **Description**: Update an existing review
- **Note**: Sets `is_edited` to true

#### Delete review
- **URL**: `/api/reviews/<id>/`
- **Method**: `DELETE`
- **Permission**: Owner or admin only
- **Description**: Delete a review

#### Like a review
- **URL**: `/api/reviews/<id>/like/`
- **Method**: `POST`
- **Permission**: Authenticated only
- **Description**: Add or update a like reaction to a review
- **Response**: `{"message": "Liked"}`

#### Dislike a review
- **URL**: `/api/reviews/<id>/dislike/`
- **Method**: `POST`
- **Permission**: Authenticated only
- **Description**: Add or update a dislike reaction to a review
- **Response**: `{"message": "Disliked"}`

#### Remove reaction from review
- **URL**: `/api/reviews/<id>/reaction/`
- **Method**: `DELETE`
- **Permission**: Authenticated only
- **Description**: Remove the current user's reaction from a review
- **Response**: `{"message": "Reaction removed"}`

---

## 🔍 Filter System

All list endpoints support filtering through query parameters.

### Series Filters
- **genre**: Filter by genre (shonen, seinen, shojo)
  - Example: `/api/series?genre=shonen`
- **title**: Filter by title (exact match)
  - Example: `/api/series?title=One Piece`
- **ongoing**: Filter by publication status
  - `ongoing=true`: Series still being published
  - `ongoing=false`: Completed series
  - Example: `/api/series?ongoing=true`
- **average_rating_min**: Minimum average rating
  - Example: `/api/series?average_rating_min=4`
- **average_rating_max**: Maximum average rating
  - Example: `/api/series?average_rating_max=5`

### Author Filters
- **name**: Filter by author name
  - Example: `/api/authors?name=Eiichiro Oda`

### Chapter Filters
- **manga**: Filter by manga ID
  - Example: `/api/chapters?manga=1`
- **number**: Filter by chapter number
  - Example: `/api/chapters?number=10`

### Review Filters
- **user**: Filter by user ID
  - Example: `/api/reviews?user=1`
- **chapter**: Filter by chapter ID
  - Example: `/api/reviews?chapter=1`
- **parent**: Filter by parent review ID (for comments)
  - Example: `/api/reviews?parent=1`

### Profile Filters
- Standard filtering available on profile fields

---

## 📊 Order System

All list endpoints support ordering through the `ordering` query parameter.

### Series Ordering
- **title**: Alphabetical order by title
  - Example: `/api/series?ordering=title`
- **first_published**: Order by first publication date
  - Example: `/api/series?ordering=first_published`
- **average_rating**: Order by average rating
  - Example: `/api/series?ordering=average_rating`
- **count_rating**: Order by number of ratings
  - Example: `/api/series?ordering=count_rating`

### Author Ordering
- **name**: Alphabetical order by name
  - Example: `/api/authors?ordering=name`
- **birth_day**: Order by birth date
  - Example: `/api/authors?ordering=birth_day`

### Chapter Ordering
- **first_published**: Order by publication date
  - Example: `/api/chapters?ordering=first_published`
- **manga**: Order by manga ID
  - Example: `/api/chapters?ordering=manga`
- **average_rating**: Order by average rating
  - Example: `/api/chapters?ordering=average_rating`

### Review Ordering
- **created_at**: Order by creation date (default: descending)
  - Example: `/api/reviews?ordering=created_at`
- **rating**: Order by rating
  - Example: `/api/reviews?ordering=rating`

**Note**: Prefix with `-` for descending order (e.g., `ordering=-title`)

---

## 🏷️ Data Models

### Manga Data Models
- **Author**: name, birth_day, death_date, image
- **Serie**: title, first_published, last_published, description, cover, genre, authors (many-to-many)
- **Chapter**: number, name, manga (foreign key), first_published

### User Data Models
- **User**: Standard Django user fields
- **Profile**: user (one-to-one), bio, profile_picture, mangas (many-to-many to Chapter)
- **Review**: user, rating (1-5), description, chapter, parent (for comments), is_edited, created_at
- **ReviewReaction**: user, review, reaction (like/dislike)

---

## 🔐 Permissions

- **Read operations**: Public (no authentication required)
- **Write operations**: Admin only (for manga data)
- **User-specific operations**: Owner or admin only
- **Authentication required**: For user profiles, reviews, and reactions

---

## 📝 Examples

### Get all shonen series ordered by rating
```
GET /api/series?genre=shonen&ordering=-average_rating
```

### Get all chapters for a specific manga
```
GET /api/chapters?manga=1&ordering=number
```

### Get all reviews for a chapter
```
GET /api/reviews?chapter=1&ordering=-created_at
```

### Create a new review
```
POST /api/reviews/
Content-Type: application/json

{
  "chapter": 1,
  "rating": 5,
  "description": "This chapter was amazing!"
}
```

### Add manga to collection
```
POST /api/profiles/add_manga/
Content-Type: application/json

{
  "chapter": 1
}
```

### Like a review
```
POST /api/reviews/1/like/
```

---

## 🛠️ Health Check

- **URL**: `/health/`
- **Method**: `GET`
- **Description**: Check if the API is running
- **Response**: `{"status": "ok"}`

---

## 📁 Media Files

Media files (images) are served at `/media/` in debug mode and include:
- Author images: `/media/authors/<year>/<month>/<day>/<filename>`
- Series covers: `/media/series/<year>/<month>/<day>/<filename>`
- Profile pictures: `/media/profile_picture/<filename>`
