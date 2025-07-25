from func import table_to_csv_string, get_page, merge_infos_to_csv, normalize_csv
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
    OUTPUT_PATH = os.path.join("output")
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    for table in tables:
        fileprefix = f"{table}"
        with open(os.path.join(OUTPUT_PATH, fileprefix+".csv"), "w+", encoding="utf-8") as c:
            c.write(table_to_csv_string(get_page(URLs[table])))
        
        normalize_csv(os.path.join(OUTPUT_PATH, fileprefix+".csv"))
        if "list-univ-priv" in fileprefix:
            merge_infos_to_csv(os.path.join(OUTPUT_PATH, fileprefix+".csv"), os.path.join(OUTPUT_PATH, fileprefix+"-full.csv"))
