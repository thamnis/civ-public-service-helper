"""
justice_services/main.py

Interface en ligne de commande pour le portail e-Justice (Casier Judiciaire).
"""

import sys
import argparse
import json

try:
    from .scraper import check_demande_status
except ImportError:
    from scraper import check_demande_status

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def main():
    parser = argparse.ArgumentParser(description="e-Justice Services CLI (Casier Judiciaire)")
    parser.add_argument("--demande", type=str, required=True, help="Numéro de la demande de casier judiciaire")
    parser.add_argument("--cookie", type=str, default="", help="Cookie de session (requis si le portail exige une authentification)")
    parser.add_argument("--save-json", type=str, help="Sauvegarder le résultat dans un fichier JSON")

    args = parser.parse_args()

    print(f"🔍 VÉRIFICATION STATUT E-JUSTICE - (Demande: {args.demande})")
    print("=" * 60)

    res = check_demande_status(args.demande, args.cookie)

    if res.get("status") == "success":
        print(f"✅ Résultat : {res.get('message')}")
    elif res.get("status") == "offline":
        print(f"📡 ERREUR RESEAU/HORS-LIGNE : {res.get('message')}")
    else:
        print(f"⚠️ {res.get('status').upper()} : {res.get('message')}")

    if args.save_json:
        with open(args.save_json, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print(f"📁 Résultat sauvegardé dans {args.save_json}")


if __name__ == "__main__":
    main()
