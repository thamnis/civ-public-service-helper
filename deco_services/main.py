"""
deco_services/main.py

Interface en ligne de commande pour interroger les résultats du CEPE et du BEPC (DECO).
"""

import sys
import argparse
import json

try:
    from .scraper import get_bepc_result, get_cepe_result
except ImportError:
    from scraper import get_bepc_result, get_cepe_result

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def main():
    parser = argparse.ArgumentParser(description="DECO Services CLI (Résultats BEPC / CEPE)")
    parser.add_argument("--exam", type=str, required=True, choices=["bepc", "cepe"], help="L'examen à vérifier (bepc ou cepe)")
    parser.add_argument("--matricule", type=str, required=True, help="Matricule du candidat")
    parser.add_argument("--save-json", type=str, help="Sauvegarder le résultat dans un fichier JSON")

    args = parser.parse_args()

    print(f"🔍 RECHERCHE RÉSULTAT {args.exam.upper()} (Matricule: {args.matricule})")
    print("=" * 60)

    if args.exam == "bepc":
        res = get_bepc_result(args.matricule)
    else:
        res = get_cepe_result(args.matricule)

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
