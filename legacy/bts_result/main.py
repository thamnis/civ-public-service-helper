"""
bts_result/main.py

Point d'entrée principal pour tester et exécuter le scrapper de résultats BTS.
Supporte l'interrogation unitaire, le calendrier officiel, les statistiques, les filières et le traitement par lot.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any

# Import relatif ou absolu
try:
    from .scraper import (
        get_bts_result,
        get_bts_calendar,
        get_bts_statistics,
        get_bts_filieres,
        download_bts_convocation,
        normalize_birthdate,
    )
except ImportError:
    from scraper import (
        get_bts_result,
        get_bts_calendar,
        get_bts_statistics,
        get_bts_filieres,
        download_bts_convocation,
        normalize_birthdate,
    )

# Pour s'assurer de l'affichage correct des caractères accentués et emojis sous Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def display_candidate_result(res: Dict[str, Any]) -> None:
    print("=" * 60)
    print("🎓 RÉSULTATS D'ADMISSIBILITÉ AU BTS (MESRS)")
    print("=" * 60)
    if res.get("status") == "success":
        decision_emoji = "🎉" if res.get("is_admitted") else "❌"
        print(f"{decision_emoji} Statut      : {'ADMISSIBLE' if res.get('is_admitted') else 'REFUSÉ'}")
        print(f"👤 Nom         : {res.get('full_name')}")
        print(f"🆔 BTS ID      : {res.get('bts_id')}")
        print(f"🆔 Matricule   : {res.get('student_id')}")
        print(f"📅 Né(e) le    : {res.get('birthdate')} à {res.get('birthplace')}")
        print(f"📚 Filière     : {res.get('sector')}")
        print(f"🏛️ Session     : {res.get('session')}")
        print(f"💬 Message     : {res.get('message')}")
    else:
        print(f"⚠️ Résultat    : {res.get('message')}")
    print("-" * 60)


def scrape_from_file(json_file_path: str) -> Dict[str, Any]:
    """
    Charge les candidats depuis un fichier JSON et récupère leurs résultats BTS.
    """
    if not os.path.exists(json_file_path):
        print(f"❌ Fichier non trouvé : {json_file_path}")
        return {}

    with open(json_file_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    from requests import Session
    session = Session()

    results = {}
    print(f"🔍 Traitement de {len(candidates)} candidat(s) depuis {json_file_path}...\n")

    for key, cand in candidates.items():
        matricule = cand.get("student_id") or cand.get("bts_id")
        birthdate = cand.get("birthdate")

        print(f"➡️ Candidat #{key} : {cand.get('first_name', '')} {cand.get('last_name', '')} ({matricule})")
        res = get_bts_result(matricule, birthdate, session=session)
        results[key] = res
        display_candidate_result(res)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Scraper et utilitaires BTS Côte d'Ivoire (https://bts.mesrs-ci.net)"
    )
    parser.add_argument("--id", type=str, help="Matricule permanent ou identifiant BTS (ex: DOJO010100001)")
    parser.add_argument("--birthdate", type=str, help="Date de naissance (ex: 01/01/2000 ou 2000-01-01)")
    parser.add_argument("--calendar", action="store_true", help="Afficher le calendrier officiel de la session")
    parser.add_argument("--stats", action="store_true", help="Afficher les statistiques nationales de la session")
    parser.add_argument("--filieres", action="store_true", help="Afficher la liste des filières industrielles et tertiaires")
    parser.add_argument("--convocation", action="store_true", help="Télécharger la convocation BTS pour le matricule spécifié")
    parser.add_argument("--output-dir", type=str, default="downloads/bts-convoc", help="Dossier de téléchargement pour la convocation")
    parser.add_argument("--file", type=str, help="Chemin vers un fichier JSON de candidats")
    parser.add_argument("--save-json", type=str, help="Sauvegarder le résultat dans un fichier JSON")

    args = parser.parse_args()

    # 1. Calendrier
    if args.calendar:
        print("📅 CALENDRIER OFFICIEL DE LA SESSION BTS (MESRS)")
        print("=" * 65)
        cal = get_bts_calendar()
        if cal.get("status") == "success":
            for ev in cal.get("events", []):
                print(f"• {ev['etape']}")
                print(f"  👉 {ev['periode']}\n")
        else:
            print(f"⚠️ {cal.get('message')}")
        return

    # 2. Statistiques
    if args.stats:
        print("📊 STATISTIQUES NATIONALES DE L'EXAMEN BTS")
        print("=" * 65)
        stats = get_bts_statistics()
        if stats.get("status") == "success":
            for k, v in stats.get("statistics", {}).items():
                print(f"• {k.replace('_', ' ').capitalize()} : {v}")
        else:
            print(f"⚠️ {stats.get('message')}")
        return

    # 3. Filières
    if args.filieres:
        print("📚 FILIÈRES ET SPÉCIALITÉS OFFICIELLES DU BTS")
        print("=" * 65)
        fils = get_bts_filieres()
        if fils.get("status") == "success":
            print(f"\n🏭 FILIÈRES INDUSTRIELLES ({len(fils.get('industrielles', []))}) :")
            for f in fils.get("industrielles", []):
                print(f"  - [{f['sigle']}] {f['libelle']}")
            print(f"\n🏢 FILIÈRES TERTIAIRES ({len(fils.get('tertiaires', []))}) :")
            for f in fils.get("tertiaires", []):
                print(f"  - [{f['sigle']}] {f['libelle']}")
        else:
            print("⚠️ Erreur lors de la récupération des filières.")
        return

    # 4. Télécharger convocation
    if args.convocation:
        if not args.id:
            print("❌ Veuillez fournir un matricule avec --id pour télécharger la convocation.")
            return
        print(f"📥 Téléchargement de la convocation BTS pour {args.id}...")
        dl_res = download_bts_convocation(args.id, output_dir=args.output_dir)
        if dl_res.get("status") == "success":
            print(f"✅ Convocation téléchargée : {dl_res['file_path']} ({dl_res['file_size']} octets)")
        else:
            print(f"⚠️ {dl_res.get('message')}")
        return

    # 5. Candidat individuel
    if args.id:
        if not args.birthdate:
            print("❌ Le paramètre --birthdate est requis pour consulter le résultat d'un candidat.")
            return
        res = get_bts_result(args.id, args.birthdate)
        display_candidate_result(res)
        if args.save_json:
            with open(args.save_json, "w", encoding="utf-8") as f:
                json.dump(res, f, ensure_ascii=False, indent=4)
            print(f"💾 Résultat sauvegardé dans {args.save_json}")
        return

    # 6. Mode Fichier ou data.json par défaut
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_file = args.file or os.path.join(current_dir, "data.json")

    results = scrape_from_file(target_file)
    output_path = args.save_json or os.path.join(current_dir, "results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"\n✅ Résultats sauvegardés dans {output_path}")


if __name__ == "__main__":
    main()

