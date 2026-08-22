"""
infas_convocation/main.py

Point d'entrée principal pour tester et exécuter le scraper / téléchargeur de convocations INFAS.
Supporte l'interrogation unitaire et le traitement par lot (batch) à partir d'un fichier JSON.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any
from requests import Session

# Import relatif ou absolu selon le mode d'exécution
try:
    from .scraper import (
        get_infas_convocation,
        download_infas_convocation,
        extract_infas_pdf_info,
        clean_candidate_code,
    )
except ImportError:
    from scraper import (
        get_infas_convocation,
        download_infas_convocation,
        extract_infas_pdf_info,
        clean_candidate_code,
    )

# Assure l'affichage correct des caractères accentués et emojis sous Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def display_result(res: Dict[str, Any]) -> None:
    """
    Affiche de façon élégante le résultat de convocation d'un candidat INFAS.
    """
    code = res.get("candidate_id", "N/A")
    if res.get("status") != "success":
        print(f"❌ [{code}] Erreur : {res.get('message')}")
        return

    print("=" * 65)
    print(f"🏥 CONCOURS INFAS  |  CANDIDAT : {code}")
    print("=" * 65)
    print(f"👤 Nom complet     : {res.get('full_name', 'N/A')}")
    print(f"🔢 Numéro de table : {res.get('table_number', 'N/A')}")
    if res.get("birthdate"):
        print(f"📅 Naissance       : {res.get('birthdate')} à {res.get('birthplace', 'N/A')}")
    if res.get("id_card"):
        print(f"🪪 Pièce d'identité: {res.get('id_card')}")

    sessions = res.get("sessions", [])
    if sessions:
        print("\n📝 DÉTAILS DES ÉPREUVES / SESSIONS :")
        for idx, sess in enumerate(sessions, 1):
            print(f"   [{idx}] Concours : {sess.get('concours')}")
            print(f"       Centre   : {sess.get('centre')}")
            print(f"       Salle    : {sess.get('salle')}")
            print(f"       Date     : {sess.get('date')} à {sess.get('heure')}")
    else:
        print("\nℹ️  Aucune session d'épreuve détaillée trouvée.")

    pdf_info = res.get("pdf")
    if pdf_info and pdf_info.get("status") == "success":
        print(f"\n📄 Fiche PDF       : {pdf_info.get('file_path')} ({pdf_info.get('file_size')} octets)")

    print("-" * 65)


def scrape_from_file(json_file_path: str, download_pdf: bool = False, output_dir: str = "downloads/infas") -> Dict[str, Any]:
    """
    Charge les candidats depuis un fichier JSON et récupère leurs convocations.
    """
    if not os.path.exists(json_file_path):
        print(f"❌ Fichier non trouvé : {json_file_path}")
        return {}

    with open(json_file_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    session = Session()
    results = {}
    print(f"\n🔍 Traitement de {len(candidates)} candidat(s) depuis {json_file_path}...\n")

    for key, cand in candidates.items():
        if isinstance(cand, dict):
            student_id = cand.get("student_id") or cand.get("code") or cand.get("candidate_id")
        else:
            student_id = str(cand)

        if not student_id:
            continue

        res = get_infas_convocation(
            student_id,
            download_pdf=download_pdf,
            output_dir=output_dir,
            session=session,
        )
        results[key] = res
        display_result(res)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Scraper et téléchargeur de convocations au concours INFAS (https://infas.ciconcours.com)"
    )
    parser.add_argument(
        "--id",
        type=str,
        help="Numéro de candidature INFAS à consulter (ex: CD00000000 ou CA00000000)",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Télécharger automatiquement la convocation officielle en format PDF",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="downloads/infas",
        help="Répertoire de destination pour les fichiers PDF (défaut: downloads/infas)",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Chemin vers un fichier JSON contenant une liste de candidats",
    )
    parser.add_argument(
        "--save-json",
        type=str,
        help="Sauvegarder les résultats complets dans un fichier JSON de sortie",
    )

    args = parser.parse_args()

    # Mode 1 : Numéro candidat unique
    if args.id:
        print(f"🔍 Consultation pour le candidat INFAS : {args.id}")
        res = get_infas_convocation(
            args.id,
            download_pdf=args.download,
            output_dir=args.output_dir,
        )
        display_result(res)

        if args.save_json:
            with open(args.save_json, "w", encoding="utf-8") as f:
                json.dump(res, f, ensure_ascii=False, indent=4)
            print(f"💾 Résultat sauvegardé dans {args.save_json}")
        return

    # Mode 2 : Fichier JSON spécifié ou data.json par défaut
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_file = args.file or os.path.join(current_dir, "data.json")

    results = scrape_from_file(
        target_file,
        download_pdf=args.download,
        output_dir=args.output_dir,
    )

    output_path = args.save_json or os.path.join(current_dir, "results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"\n✅ Résultats complets sauvegardés dans : {output_path}")


if __name__ == "__main__":
    main()
