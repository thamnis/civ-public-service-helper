"""
oneci_services/main.py

Interface en ligne de commande pour interroger les services de l'ONECI.
"""

import sys
import argparse
import json

try:
    from .scraper import check_cni_status, find_numero_demande
except ImportError:
    from scraper import check_cni_status, find_numero_demande

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def main():
    parser = argparse.ArgumentParser(description="ONECI Services CLI")
    
    # Subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")
    
    # Command: statut
    parser_statut = subparsers.add_parser("statut", help="Vérifier le statut d'une demande CNI/CRC")
    parser_statut.add_argument("--numero", type=str, required=True, help="Numéro de demande (10-14 caractères)")
    parser_statut.add_argument("--nom", type=str, required=True, help="Nom de famille")
    parser_statut.add_argument("--dnaiss", type=str, required=True, help="Date de naissance (YYYY-MM-DD)")
    parser_statut.add_argument("--titre", type=str, default="CNI", choices=["CNI", "CRC"], help="Titre de la demande (CNI ou CRC)")
    parser_statut.add_argument("--token", type=str, default="", help="Jeton reCAPTCHA v3 (optionnel mais recommandé)")
    parser_statut.add_argument("--save-json", type=str, help="Sauvegarder le résultat dans un fichier JSON")

    # Command: find_numero
    parser_find = subparsers.add_parser("find_numero", help="Retrouver un numéro de demande perdu")
    parser_find.add_argument("--nom", type=str, required=True, help="Nom de famille")
    parser_find.add_argument("--prenoms", type=str, required=True, help="Prénoms")
    parser_find.add_argument("--dnaiss", type=str, required=True, help="Date de naissance (YYYY-MM-DD)")
    parser_find.add_argument("--lnaiss", type=str, required=True, help="Lieu de naissance (ex: ABIDJAN)")
    parser_find.add_argument("--titre", type=str, default="CNI", choices=["CNI", "CRC"], help="Titre de la demande (CNI ou CRC)")
    parser_find.add_argument("--token", type=str, default="", help="Jeton reCAPTCHA v3 (optionnel mais recommandé)")
    parser_find.add_argument("--save-json", type=str, help="Sauvegarder le résultat dans un fichier JSON")

    args = parser.parse_args()

    if args.command == "statut":
        print(f"🔍 VÉRIFICATION STATUT ONECI ({args.titre} - {args.numero})")
        print("=" * 65)
        res = check_cni_status(
            numero_demande=args.numero,
            nom=args.nom,
            date_naissance=args.dnaiss,
            titre=args.titre,
            recaptcha_token=args.token
        )
        if res.get("status") == "success":
            print(f"✅ Succès : {res.get('message')}")
        else:
            print(f"⚠️ {res.get('status').upper()} : {res.get('message')}")

        if args.save_json:
            with open(args.save_json, "w", encoding="utf-8") as f:
                json.dump(res, f, ensure_ascii=False, indent=2)
            print(f"📁 Résultat sauvegardé dans {args.save_json}")

    elif args.command == "find_numero":
        print(f"🔍 RECHERCHE NUMÉRO DE DEMANDE ONECI ({args.titre} - {args.nom} {args.prenoms})")
        print("=" * 65)
        res = find_numero_demande(
            nom=args.nom,
            prenoms=args.prenoms,
            date_naissance=args.dnaiss,
            lieu_naissance=args.lnaiss,
            titre=args.titre,
            recaptcha_token=args.token
        )
        if res.get("status") == "success":
            print(f"✅ Succès : {res.get('message')}")
        else:
            print(f"⚠️ {res.get('status').upper()} : {res.get('message')}")

        if args.save_json:
            with open(args.save_json, "w", encoding="utf-8") as f:
                json.dump(res, f, ensure_ascii=False, indent=2)
            print(f"📁 Résultat sauvegardé dans {args.save_json}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
