import csv
import psycopg
from variables import db_name, user

def main():
    # connect to database
    with psycopg.connect(f"dbname={db_name} user={user}") as conn:
        with conn.cursor() as cur:
            # get csv by row
            with open('./csv/author.csv', 'r') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                for row in csv_reader:
                    if row["death_date"] == "":
                        row["death_date"] = None
                    cur.execute(
                        "INSERT INTO mangas_author (name, birth_day, death_date) VALUES (%s, %s, %s)",
                        (row["name"], row["birth_day"], row["death_date"])
                    )
                    print(f"{row["name"]} has been added to the author table")

main()