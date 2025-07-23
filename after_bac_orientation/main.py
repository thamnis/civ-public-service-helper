from func import table_to_csv_string, get_page
import os

URLs = {
    "home": "https://bac.mesrs-ci.net/",
    "list-univ-priv": "https://bac.mesrs-ci.net/offres/ets-prives",
    "ranking-bts": "https://bac.mesrs-ci.net/classement/bts2022",
    "ranking-college": "https://bac.mesrs-ci.net/classement/grdes-ecoles",
    "ranking-university": "https://bac.mesrs-ci.net/classement/grdes-ecoles",
    "guide-orientation": "https://bac.mesrs-ci.net/classement/grdes-ecoles",
    "verif-perso_data": "https://bac.mesrs-ci.net/classement/grdes-ecoles"
}

tables = ["list-univ-priv", "ranking-bts", "ranking-college", "ranking-university"]
if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    for table in tables:
        with open(os.path.join("output", f"{table}.csv"), "w+", encoding="utf-8") as c:
            c.write(table_to_csv_string(get_page(URLs[table])))
