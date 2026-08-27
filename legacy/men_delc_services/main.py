import argparse
import json
import sys

from .scraper import (
    get_textes_officiels,
    get_drena_directory,
    get_iepp_directory,
    get_primaire_nominations
)

def main():
    parser = argparse.ArgumentParser(description="Service MEN-DELC (Textes officiels, Annuaires, Nominations)")
    
    parser.add_argument('--textes', action='store_true', help="Récupérer tous les textes officiels")
    parser.add_argument('--drena', action='store_true', help="Récupérer l'annuaire des DRENA")
    parser.add_argument('--iepp', action='store_true', help="Récupérer l'annuaire des IEPP")
    parser.add_argument('--nominations', choices=['directeur', 'maitre_application'], help="Récupérer les nominations")
    
    args = parser.parse_args()

    if args.textes:
        res = get_textes_officiels()
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0)

    if args.drena:
        res = get_drena_directory()
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0)

    if args.iepp:
        res = get_iepp_directory()
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0)

    if args.nominations:
        res = get_primaire_nominations(args.nominations)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0)

    parser.print_help()

if __name__ == "__main__":
    main()
