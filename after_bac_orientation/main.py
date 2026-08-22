"""
after_bac_orientation/main.py

Point d'entrée principal pour tester et exécuter les outils d'orientation post-BAC (bac.mesrs-ci.net).
"""

import os
import sys
import json
import argparse
from typing import Dict, Any

try:
    from .scraper import (
        get_bac_orientation_concours,
        get_bac_orientation_concours_admissibles,
        check_bac_orientation_payment,
        simulate_bac_orientation,
        get_bac_etablissement_sectors,
    )
except ImportError:
    from scraper import (
        get_bac_orientation_concours,
        get_bac_orientation_concours_admissibles,
        check_bac_orientation_payment,
        simulate_bac_orientation,
        get_bac_etablissement_sectors,
    )

# Assure l'affichage correct des caractères accentués sous Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def main():
    parser = argparse.ArgumentParser(
        description="Scraper et utilitaires d'orientation post-BAC (https://bac.mesrs-ci.net)"
    )
    parser.add_argument("--concours", action="store_true", help="Lister tous les concours d'orientation spéciaux")
    parser.add_argument("--admissibles", type=str, help="ID du concours dont afficher les admissibles (ex: 20693)")
    parser.add_argument("--payment", type=str, help="Vérifier le statut de paiement pour un matricule BAC")
    parser.add_argument("--simulate", type=str, help="Simuler l'orientation pour un matricule BAC")
    parser.add_argument("--sectors", type=str, help="Code établissement dont afficher les filières")
    parser.add_argument("--save-json", type=str, help="Sauvegarder le résultat dans un fichier JSON")

    args = parser.parse_args()

    # 1. Liste des concours
    if args.concours:
        print("🏛️ CONCOURS D'ORIENTATION POST-BAC (MESRS)")
        print("=" * 65)
        res = get_bac_orientation_concours()
        if res.get("status") == "success":
            for c in res.get("concours", []):
                print(f"• [ID: {c['id']}] {c['title']} 👉 {c['url']}")
        else:
            print(f"⚠️ {res.get('message')}")
        return

    # 2. Admissibles à un concours
    if args.admissibles:
        print(f"📋 CANDIDATS ADMISSIBLES AU CONCOURS #{args.admissibles}")
        print("=" * 65)
        res = get_bac_orientation_concours_admissibles(args.admissibles)
        if res.get("status") == "success":
            print(f"🎓 Titre : {res.get('title')}")
            print(f"👥 Total : {res.get('count')} admissible(s)\n")
            for cand in res.get("admissibles", [])[:20]:
                print(f"  {cand['rang']}. {cand['nom_prenoms']}")
            if res.get("count", 0) > 20:
                print(f"\n  ... et {res.get('count') - 20} autre(s) candidat(s).")
        else:
            print(f"⚠️ {res.get('message')}")
        return

    # 3. Vérification de paiement
    if args.payment:
        print(f"💳 VÉRIFICATION PAIEMENT ORIENTATION BAC ({args.payment})")
        print("=" * 65)
        res = check_bac_orientation_payment(args.payment)
        if res.get("status") == "success":
            print("✅ Paiement enregistré avec succès !")
        else:
            print(f"⚠️ {res.get('message')}")
        return

    # 4. Simulation
    if args.simulate:
        print(f"🎯 SIMULATEUR D'ORIENTATION BAC ({args.simulate})")
        print("=" * 65)
        res = simulate_bac_orientation(args.simulate)
        print(res.get("message"))
        return

    # 5. Filières établissement
    if args.sectors:
        print(f"🏫 FILIÈRES ÉTABLISSEMENT ({args.sectors})")
        print("=" * 65)
        res = get_bac_etablissement_sectors(args.sectors)
        print(res)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
