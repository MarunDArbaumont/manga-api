import csv
import os
import psycopg
from variables import db_name, user

def main():
    csv_dir_path = "./csv"
    dir_list = os.listdir(csv_dir_path)
    print(f"Files in csv : {dir_list}")
    with psycopg.connect(f"dbname={db_name} user={user}") as conn:
        with conn.cursor() as cur:
            for file in dir_list:
                print(f"{file} is being processed")
                with open(f"./csv/{file}", "r") as csvfile:
                    csv_reader = csv.DictReader(csvfile, delimiter=";")
                    if file == "author.csv":
                        for row in csv_reader:
                            if row["death_date"] == "":
                                row["death_date"] = None
                            cur.execute(
                                "INSERT INTO mangas_author (name, birth_day, death_date) VALUES (%s, %s, %s)",
                                (row["name"], row["birth_day"], row["death_date"])
                            )
                            print(f"{row['name']} has been added to the author table")
                    elif file == "serie.csv":
                        for row in csv_reader:
                            if row["last_published"] == "":
                                row["last_published"] = None
                            cur.execute(
                                "INSERT INTO mangas_serie (title, first_published, last_published, description) VALUES (%s, %s, %s, %s)",
                                (row["title"], row["first_published"], row["last_published"], row["description"])
                            )
                            print(f"{row['title']} has been added to the serie table")
                    elif "chapter" in file:
                        for row in csv_reader:
                                cur.execute(
                                    "INSERT INTO mangas_chapter (number, name, first_published, manga_id) VALUES (%s, %s, %s, %s)",
                                    (row["number"], row["name"], row["first_published"], row["manga_id"])
                                )
                                print(f"N°{row["number"]}: {row["name"]} has been added to the chapter table")
                    else:
                        print(f"{file} is not a valid syntax for file name")
            conn.commit()
            print("\n Import completed successfully")

main()