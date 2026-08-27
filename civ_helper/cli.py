"""
civ_helper/cli.py

Point d'entrée unique en ligne de commande pour civ-public-service-helper.
"""

import argparse
import sys
import json

from .services import deco, cei, mfp, justice, oneci
from .core.exceptions import CivHelperError

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def execute_service(service_name: str, func, *args, **kwargs):
    print(f"🔍 [CIV-HELPER] RECHERCHE EN COURS : {service_name}")
    print("=" * 60)
    try:
        res = func(*args, **kwargs)
        if res.get("status") == "success":
            print(f"✅ Résultat : {res.get('message')}")
        else:
            print(f"⚠️ {res.get('status', 'inconnu').upper()} : {res.get('message')}")
    except CivHelperError as e:
        print(f"❌ ERREUR SDK : {e}")
    except Exception as e:
        print(f"🚨 ERREUR CRITIQUE : {e}")


def main():
    parser = argparse.ArgumentParser(description="civ-helper : Outil unifié pour les services publics Ivoiriens")
    subparsers = parser.add_subparsers(dest="service", required=True)

    # ------------------ DECO ------------------
    parser_deco = subparsers.add_parser("deco", help="Examens Scolaires (BEPC, CEPE)")
    parser_deco.add_argument("--exam", required=True, choices=["bepc", "cepe"])
    parser_deco.add_argument("--matricule", required=True)

    # ------------------ CEI ------------------
    parser_cei = subparsers.add_parser("cei", help="Commission Électorale (Liste électorale)")
    parser_cei.add_argument("--voter", required=True, help="Numéro CNI / Récépissé")

    # ------------------ MFP ------------------
    parser_mfp = subparsers.add_parser("mfp", help="Fonction Publique (Concours)")
    parser_mfp.add_argument("--concours", required=True, help="Numéro d'inscription")

    # ------------------ JUSTICE ------------------
    parser_justice = subparsers.add_parser("justice", help="e-Justice (Casier Judiciaire)")
    parser_justice.add_argument("--demande", required=True)
    parser_justice.add_argument("--cookie", default="")

    # ------------------ ONECI ------------------
    parser_oneci = subparsers.add_parser("oneci", help="ONECI (CNI)")
    parser_oneci.add_argument("--numero", required=True)
    parser_oneci.add_argument("--nom", required=True)
    parser_oneci.add_argument("--date-naissance", required=True)
    parser_oneci.add_argument("--titre", default="CNI")
    parser_oneci.add_argument("--token", default="")

    args = parser.parse_args()

    if args.service == "deco":
        if args.exam == "bepc":
            execute_service("DECO - BEPC", deco.get_bepc_result, args.matricule)
        else:
            execute_service("DECO - CEPE", deco.get_cepe_result, args.matricule)

    elif args.service == "cei":
        execute_service("CEI - Liste Électorale", cei.check_voter_status, args.voter)

    elif args.service == "mfp":
        execute_service("MFP - Concours", mfp.get_concours_result, args.concours)

    elif args.service == "justice":
        execute_service("e-Justice - Casier", justice.check_demande_status, args.demande, session_cookie=args.cookie)

    elif args.service == "oneci":
        execute_service("ONECI - Statut", oneci.check_cni_status, args.numero, args.nom, args.date_naissance, args.titre, args.token)


if __name__ == "__main__":
    main()
