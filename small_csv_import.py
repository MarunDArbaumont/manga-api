import csv
import os
import psycopg
from variables import DB_NAME, USER, TABLE_PREFIX

def sql_injection(row, table_name):
    injection = f"INSERT INTO {table_name} ("
    values = " VALUES("
    i = 1
    for key, data in row.items():
        if i < len(row):
            if data == "":
                values += "NULL" + ", "
            else:
                values += "'" + data + "', "
            injection += key + ", "
            i += 1
            continue
        injection += key + ")"
        values += "'" + data + "')"
    final_injection = injection + values
    print(final_injection)
    return final_injection

def main():
    csv_dir_path = "./csv"
    dir_list = os.listdir(csv_dir_path)
    only_csv = filter(lambda x : x.endswith(".csv"), dir_list)
    print(f"Files in csv : {only_csv}")
    with psycopg.connect(f"dbname={DB_NAME} user={USER}") as conn:
        with conn.cursor() as cur:
            for file in only_csv:
                print(f"{file} is being processed")
                with open(f"./csv/{file}", "r") as csvfile:
                    csv_reader = csv.DictReader(csvfile, delimiter=";")
                    for row in csv_reader:
                        db_table = TABLE_PREFIX + file[:-4]
                        first = next(iter(row))
                        cur.execute(
                            sql_injection(row, db_table)
                        )
                        print(f"{row[first]} has been added to the author table")
            conn.commit()
            print("\n Import completed successfully")

main()