"""
sigfne_documents/main.py

Point d'entrée principal pour tester et exécuter le téléchargeur de documents scolaires SIGFNE.
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
        download_sigfne_document,
        get_sigfne_document,
        extract_pdf_info,
        DOCUMENT_TYPES,
        ACADEMIC_YEARS,
        clean_student_code,
    )
except ImportError:
    from scraper import (
        download_sigfne_document,
        get_sigfne_document,
        extract_pdf_info,
        DOCUMENT_TYPES,
        ACADEMIC_YEARS,
        clean_student_code,
    )

# Assure l'affichage correct des caractères accentués et emojis sous Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def display_result(res: Dict[str, Any]) -> None:
    """
    Affiche de façon claire le résultat de téléchargement du document SIGFNE.
    """
    code = res.get("matricule", "N/A")
    doc_label = res.get("doc_label", res.get("doc_type", "Document"))
    annee_label = res.get("annee_label", res.get("annee", "N/A"))

    print("=" * 65)
    print(f"📑 SIGFNE / DESPS  |  MATRICULE : {code}")
    print("=" * 65)
    print(f"📋 Type de document : {doc_label}")
    print(f"📅 Année scolaire   : {annee_label}")

    if res.get("status") == "success":
        print(f"✅ Statut            : TÉLÉCHARGÉ AVEC SUCCÈS")
        print(f"📄 Fichier PDF       : {res.get('file_path')}")
        print(f"📦 Taille            : {res.get('file_size')} octets")
    else:
        print(f"⚠️ Statut            : {res.get('message', 'Non disponible')}")

    print("-" * 65)


def scrape_from_file(
    json_file_path: str,
    output_dir: str = "downloads/sigfne",
) -> Dict[str, Any]:
    """
    Charge les élèves depuis un fichier JSON et télécharge leurs documents SIGFNE.
    """
    if not os.path.exists(json_file_path):
        print(f"❌ Fichier non trouvé : {json_file_path}")
        return {}

    with open(json_file_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    session = Session()
    results = {}
    print(f"\n🔍 Traitement de {len(candidates)} entrée(s) depuis {json_file_path}...\n")

    for key, cand in candidates.items():
        if isinstance(cand, dict):
            student_id = cand.get("student_id") or cand.get("matricule")
            doc_type = cand.get("doc_type", "recu")
            annee = cand.get("annee", "2627")
        else:
            student_id = str(cand)
            doc_type = "recu"
            annee = "2627"

        if not student_id:
            continue

        res = download_sigfne_document(
            student_id,
            doc_type=doc_type,
            annee=annee,
            output_dir=output_dir,
            session=session,
        )
        results[key] = res
        display_result(res)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Scraper et téléchargeur de documents scolaires SIGFNE (https://agfne.sigfne.net/vas/interface-edition-documents-sigfne/)"
    )
    parser.add_argument(
        "--id",
        type=str,
        help="Matricule de l'élève (ex: 12345678A)",
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=list(DOCUMENT_TYPES.keys()),
        default="recu",
        help="Type de document : 'recu' (reçu préinscription), 'cursus' (fiche cursus), 'cursusnew' (fiche cursus new). Défaut: recu",
    )
    parser.add_argument(
        "--annee",
        type=str,
        default="2627",
        help="Code de l'année scolaire (ex: '2627' pour 2026-2027, '2526', '2425', ...). Défaut: 2627",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="downloads/sigfne",
        help="Répertoire de destination pour les fichiers PDF (défaut: downloads/sigfne)",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Chemin vers un fichier JSON contenant une liste d'élèves",
    )
    parser.add_argument(
        "--save-json",
        type=str,
        help="Sauvegarder les résultats complets dans un fichier JSON de sortie",
    )

    args = parser.parse_args()

    # Mode 1 : Matricule unique
    if args.id:
        print(f"🔍 Requête document SIGFNE pour le matricule : {args.id}")
        res = download_sigfne_document(
            args.id,
            doc_type=args.type,
            annee=args.annee,
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
        output_dir=args.output_dir,
    )

    output_path = args.save_json or os.path.join(current_dir, "results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"\n✅ Résultats complets sauvegardés dans : {output_path}")


if __name__ == "__main__":
    main()
