import argparse
import json
import sys

from .scraper import get_cafop_affectation, get_cafop_directors_directory

def main():
    parser = argparse.ArgumentParser(description="Service CAFOP (Affectations, Annuaires)")
    
    parser.add_argument('--affectation', type=str, help="Matricule pour consulter l'affectation CAFOP")
    parser.add_argument('--directeurs', action='store_true', help="Récupérer l'annuaire des directeurs CAFOP")
    
    args = parser.parse_args()

    if args.affectation:
        res = get_cafop_affectation(args.affectation)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0)

    if args.directeurs:
        res = get_cafop_directors_directory()
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0)

    parser.print_help()

if __name__ == "__main__":
    main()
