"""
mfp_services/main.py

Interface en ligne de commande pour le MFP (Fonction Publique).
"""

import sys
import argparse
import json

try:
    from .scraper import get_concours_result
except ImportError:
    from scraper import get_concours_result

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def main():
    parser = argparse.ArgumentParser(description="MFP Services CLI (Concours Fonction Publique)")
    parser.add_argument("--concours", type=str, required=True, help="Numéro d'inscription au concours")
    parser.add_argument("--save-json", type=str, help="Sauvegarder le résultat dans un fichier JSON")

    args = parser.parse_args()

    print(f"🔍 VÉRIFICATION RÉSULTAT CONCOURS (MFP) - (Numéro: {args.concours})")
    print("=" * 60)

    res = get_concours_result(args.concours)

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
