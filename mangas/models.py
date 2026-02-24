from django.db import models

class Serie (models.Model):
    MANGA_GENRE_CHOICES = (
        ("shonen", "shonen"),
        ("seinen", "seinen"),
        ("shojo", "shojo"),
    )
    title = models.CharField(max_length=100)
    first_published = models.DateTimeField()
    last_published = models.DateTimeField(blank=True, null=True)
    description = models.CharField()
    cover = models.ImageField(blank=True, null=True, upload_to="series/%Y/%m/%d/")
    genre = models.CharField(blank=True, null=True, choices=MANGA_GENRE_CHOICES)

    def __str__(self):
        return self.title
    
    def is_finished(self):
        return self.last_published != ""


class Author (models.Model):
    name = models.CharField(max_length=100)
    birth_day = models.DateTimeField()
    death_date = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to="authors/%Y/%m/%d/")
    mangas = models.ManyToManyField(Serie, related_name="author")

    def __str__(self):
        return self.name
    
    def is_alive(self):
        return self.death_date != ""

class Chapter (models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=100)
    manga = models.ForeignKey(Serie, on_delete=models.CASCADE, related_name="chapters")
    first_published = models.DateTimeField()

    def __str__(self):
        return f"Chapter N°{self.number} {self.name} from {self.manga}"
