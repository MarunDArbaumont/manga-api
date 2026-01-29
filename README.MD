# API of mangas
The API is connected to an DB

## By author **Done**
url = /api/authors
Gets all the mangas of the author and the content (description, review, rating) 
## By serie **Done**
url = /api/series
Gets all the mangas by serie and the content (description, review, rating)
## By chapter **Done**
url = /api/chapters
Gets the content of the chapter (description, review, rating)
## CSV import **Done for small files**
Create a csv dir in the root of the project, add csv files for each table. The csv file name should have the same name as the table name minus the prefix

## Get all chapters of given manga

## Filter system **Done**
### Filter by genre **Done**
filter series by genre (shonen, seinen, shojo, action, fantasy...)
example url filter ==> api/series?genre=shonen

## Order system **To do**
### Order by alphebetic order **To do**
for series and authors
### Order by publish date **To do**
for series and authors
### Order by score **To do**
for series and authors
### Order by number of reviews / score **To do**
for series and authors
