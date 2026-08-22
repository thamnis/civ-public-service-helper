"""
mesrs_services/main.py

Point d'entrée CLI pour interroger les services du portail MESRS (inscription.mesrs-ci.net).
Supporte la vérification de paiement, la consultation des actes DEXCO, et les annonces flash.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any

try:
    from .scraper import (
        verify_mesrs_payment,
        get_mesrs_dexco_services,
        get_mesrs_announcements,
        DEXCO_DEMANDE_TYPES,
    )
except ImportError:
    from scraper import (
        verify_mesrs_payment,
        get_mesrs_dexco_services,
        get_mesrs_announcements,
        DEXCO_DEMANDE_TYPES,
    )

# Assure l'affichage correct des caractères accentués et emojis sous Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def display_payment_result(res: Dict[str, Any]) -> None:
    print("=" * 65)
    print("💳 VÉRIFICATION DU PAIEMENT MESRS (INSCRIPTION / RÉINSCRIPTION)")
    print("=" * 65)
    if res.get("status") == "success" and res.get("is_valid"):
        print("✅ Statut          : PAIEMENT VALIDÉ")
        print(f"🆔 Matricule MESRS : {res.get('matricule_mesrs')}")
        print(f"🧾 Code paiement   : {res.get('code_paiement')}")
        print(f"📱 Numéro paiement : {res.get('numero_paiement')}")
    else:
        print(f"⚠️ Statut          : {res.get('message', 'Non trouvé')}")
        print(f"🆔 Matricule MESRS : {res.get('matricule_mesrs')}")
        print(f"🧾 Code paiement   : {res.get('code_paiement')}")
    print("-" * 65)


def scrape_from_file(json_file_path: str) -> Dict[str, Any]:
    if not os.path.exists(json_file_path):
        print(f"❌ Fichier non trouvé : {json_file_path}")
        return {}

    with open(json_file_path, "r", encoding="utf-8") as f:
        entries = json.load(f)

    from requests import Session
    session = Session()
    results = {}
    print(f"\n🔍 Traitement de {len(entries)} entrée(s) depuis {json_file_path}...\n")

    for key, item in entries.items():
        mat = item.get("matricule_mesrs")
        code = item.get("code_paiement")
        num = item.get("numero_paiement")

        res = verify_mesrs_payment(mat, code, num, session=session)
        results[key] = res
        display_payment_result(res)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Scraper et utilitaires du portail MESRS (https://inscription.mesrs-ci.net)"
    )
    parser.add_argument("--matricule", type=str, help="Matricule MESRS de l'étudiant (ex: AAAB19920001)")
    parser.add_argument("--code-paiement", type=str, help="Référence / code de transaction de paiement (ex: 1502168548958751)")
    parser.add_argument("--numero-paiement", type=str, help="Numéro de téléphone / paiement (ex: 0102030405)")
    parser.add_argument("--dexco", action="store_true", help="Lister les actes administratifs et attestations DEXCO disponibles")
    parser.add_argument("--announcements", action="store_true", help="Afficher les annonces officielles et flash du MESRS")
    parser.add_argument("--file", type=str, help="Fichier JSON contenant une liste de paiements à vérifier")
    parser.add_argument("--save-json", type=str, help="Sauvegarder les résultats dans un fichier JSON")

    args = parser.parse_args()

    # 1. Annonces flash
    if args.announcements:
        print("📢 ACTUALITÉS ET ANNONCES FLASH MESRS")
        print("=" * 65)
        res = get_mesrs_announcements()
        if res.get("status") == "success":
            for idx, a in enumerate(res.get("announcements", []), 1):
                print(f"{idx}. {a}\n")
        else:
            print(f"⚠️ {res.get('message')}")
        return

    # 2. Catalogue DEXCO
    if args.dexco:
        print("📑 CATALOGUE DES ACTES D'EXAMEN & DIPLÔMES (DEXCO)")
        print("=" * 65)
        res = get_mesrs_dexco_services()
        if res.get("status") == "success":
            for s in res.get("services", []):
                print(f"• [{s['code']}] {s['label']}")
        else:
            print(f"⚠️ {res.get('message')}")
        return

    # 3. Vérification de paiement unitaire
    if args.matricule:
        if not args.code_paiement or not args.numero_paiement:
            print("❌ Les paramètres --code-paiement et --numero-paiement sont requis pour vérifier un paiement.")
            return
        res = verify_mesrs_payment(args.matricule, args.code_paiement, args.numero_paiement)
        display_payment_result(res)
        if args.save_json:
            with open(args.save_json, "w", encoding="utf-8") as f:
                json.dump(res, f, ensure_ascii=False, indent=4)
            print(f"💾 Résultat sauvegardé dans {args.save_json}")
        return

    # 4. Mode Fichier ou data.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_file = args.file or os.path.join(current_dir, "data.json")

    results = scrape_from_file(target_file)
    output_path = args.save_json or os.path.join(current_dir, "results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"\n✅ Résultats complets sauvegardés dans : {output_path}")


if __name__ == "__main__":
    main()
