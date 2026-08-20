"""
bts_result/main.py

Point d'entrée principal pour tester et exécuter le scrapper de résultats BTS.
Supporte l'interrogation unitaire et le traitement par lot (batch) à partir de data.json.
"""

import os
import sys
import json
from typing import Dict, Any
from scraper import get_bts_result, normalize_birthdate

# Pour s'assurer de l'affichage correct des caractères accentués et emojis sous Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


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

        if res.get("status") == "success":
            decision_emoji = "🎉" if res.get("is_admitted") else "❌"
            print(f"   {decision_emoji} Statut      : {'ADMISSIBLE' if res.get('is_admitted') else 'REFUSÉ'}")
            print(f"   👤 Nom         : {res.get('full_name')}")
            print(f"   🆔 BTS ID      : {res.get('bts_id')}")
            print(f"   🆔 Matricule   : {res.get('student_id')}")
            print(f"   📅 Né(e) le    : {res.get('birthdate')} à {res.get('birthplace')}")
            print(f"   📚 Filière     : {res.get('sector')}")
            print(f"   🏛️ Session     : {res.get('session')}")
            print(f"   💬 Message     : {res.get('message')}")
        else:
            print(f"   ⚠️ Résultat    : {res.get('message')}")
        print("-" * 50)

    return results


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "data.json")

    # Exemple de test avec les données par lot
    results = scrape_from_file(data_path)

    # Sauvegarde optionnelle des résultats dans results.json
    output_path = os.path.join(current_dir, "results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"\n✅ Résultats sauvegardés dans {output_path}")


if __name__ == "__main__":
    main()
