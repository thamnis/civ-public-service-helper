"""
sixieme_affectation/main.py

Point d'entrée principal pour tester et exécuter le scraper / téléchargeur d'affectation en 6ème.
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
        get_sixieme_affectation,
        download_assignment_document,
        extract_pdf_info,
        clean_student_code,
    )
except ImportError:
    from scraper import (
        get_sixieme_affectation,
        download_assignment_document,
        extract_pdf_info,
        clean_student_code,
    )

# Assure l'affichage correct des caractères accentués et emojis sous Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def display_result(res: Dict[str, Any], verbose: bool = True) -> None:
    """
    Affiche de façon élégante le résultat d'affectation d'un élève.
    """
    code = res.get("student_code", "N/A")
    if res.get("status") != "success":
        print(f"❌ [{code}] Erreur : {res.get('message')}")
        return

    student = res.get("student", {})
    school = res.get("school")
    is_assigned = res.get("is_assigned", False)

    status_badge = "🏫 AFFECTÉ(E)" if is_assigned else "⏳ NON ENCORE AFFECTÉ(E)"
    print("=" * 60)
    print(f"📌 MATRICULE : {code}  |  STATUT : {status_badge}")
    print("=" * 60)
    print(f"👤 Nom complet   : {student.get('full_name', 'N/A')}")
    print(f"📅 Naissance     : {student.get('birthday', 'N/A')} ({student.get('age', 'N/A')} ans)")
    print(f"⚧️  Genre         : {student.get('gender', 'N/A')} | Nationalité : {student.get('nationality', 'N/A')}")
    print(f"📊 TGP           : {student.get('tgp', 'N/A')}")

    if is_assigned and school:
        print("\n🏛️  ÉTABLISSEMENT D'ACCUEIL :")
        print(f"   🏢 Nom        : {school.get('school_name', 'N/A')}")
        print(f"   📍 Quartier   : {school.get('quartier', 'N/A')}")
        print(f"   🏷️  Type       : {school.get('school_type', 'N/A')}")
        print(f"   💰 Frais comp : {school.get('school_cost', '0')} FCFA")
        if school.get("free_place") is not None:
            print(f"   🪑 Places     : {school.get('assigned_count', 0)}/{school.get('capacity', 0)} (Restantes : {school.get('free_place')})")
    elif is_assigned:
        print("\n🏛️  ÉTABLISSEMENT D'ACCUEIL : Affecté (détails non disponibles)")
    else:
        print("\nℹ️  Cet(te) élève n'a pas encore d'affectation enregistrée.")

    pdf_info = res.get("pdf")
    if pdf_info and pdf_info.get("status") == "success":
        print(f"\n📄 Fiche PDF    : {pdf_info.get('file_path')} ({pdf_info.get('file_size')} octets)")

    print("-" * 60)


def scrape_from_file(json_file_path: str, download_pdf: bool = False, output_dir: str = "downloads/affectation") -> Dict[str, Any]:
    """
    Charge les élèves depuis un fichier JSON et récupère leurs affectations.
    """
    if not os.path.exists(json_file_path):
        print(f"❌ Fichier non trouvé : {json_file_path}")
        return {}

    with open(json_file_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    session = Session()
    results = {}
    print(f"\n🔍 Traitement de {len(candidates)} élève(s) depuis {json_file_path}...\n")

    for key, cand in candidates.items():
        if isinstance(cand, dict):
            student_id = cand.get("student_id") or cand.get("matricule")
        else:
            student_id = str(cand)

        if not student_id:
            continue

        res = get_sixieme_affectation(
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
        description="Scraper et téléchargeur de fiches d'affectation en 6ème (Côte d'Ivoire - affectation.mendob.ci)"
    )
    parser.add_argument(
        "--id",
        type=str,
        help="Matricule de l'élève à consulter (ex: 12345678A)",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Télécharger automatiquement la fiche d'affectation en PDF",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="downloads/affectation",
        help="Répertoire de destination pour les fichiers PDF (défaut: downloads/affectation)",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Chemin vers un fichier JSON contenant une liste d'élèves (défaut: data.json)",
    )
    parser.add_argument(
        "--save-json",
        type=str,
        help="Sauvegarder les résultats complets dans un fichier JSON de sortie",
    )

    args = parser.parse_args()

    # Mode 1 : Matricule unique passé en argument
    if args.id:
        print(f"🔍 Consultation pour le matricule : {args.id}")
        res = get_sixieme_affectation(
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
