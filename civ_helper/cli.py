"""
civ_helper/cli.py

Point d'entrée unique en ligne de commande pour civ-public-service-helper.
"""

import argparse
import sys
import json

from .services import deco, cei, mfp, justice, oneci, directory
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
        if isinstance(res, dict) and res.get("status") == "success":
            print(f"✅ Résultat : {res.get('message')}")
        elif isinstance(res, dict) and "status" in res:
            print(f"⚠️ {res.get('status', 'inconnu').upper()} : {res.get('message')}")
        else:
            print(json.dumps(res, indent=2, ensure_ascii=False))
    except CivHelperError as e:
        print(f"❌ ERREUR SDK : {e}")
    except Exception as e:
        print(f"🚨 ERREUR CRITIQUE : {e}")


def handle_directory_command(args):
    print("🏛️ [CIV-HELPER] ANNUAIRE & SANTÉ DES SERVICES PUBLICS")
    print("=" * 60)
    
    if args.health:
        target = args.health
        print(f"🩺 Test de disponibilité pour : {target}")
        res = directory.check_service_health(target)
        status_icon = "🟢" if res["status"] == "online" else ("🟡" if res["status"] == "warning" else "🔴")
        print(f"{status_icon} Nom : {res['name']}")
        print(f"   URL : {res['url']}")
        print(f"   Statut : {res['message']}")
        print(f"   Temps de réponse : {res['response_time_ms']} ms")
        return

    if args.categories:
        cats = directory.get_categories()
        print(f"📋 {len(cats)} Catégories disponibles :\n")
        for c in cats:
            print(f"  • {c['category']} ({c['count']} services)")
        return

    res = directory.get_services(
        query=args.search,
        category=args.category,
        is_eservice=True if args.eservices else None,
        limit=args.limit
    )
    
    total = res["total"]
    services = res["services"]
    
    print(f"📊 {total} service(s) trouvé(s) (Affichage de {len(services)}) :\n")
    for s in services:
        badge = " [⚡ e-Service]" if s.get("is_eservice") else ""
        print(f"🔹 [{s['id']}] {s['name']}{badge}")
        print(f"   🌐 {s['url']}")
        if s.get("description"):
            print(f"   📝 {s['description']}")
        if s.get("categories"):
            print(f"   🏷️  {', '.join(s['categories'])}")
        print("-" * 50)


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

    # ------------------ DIRECTORY ------------------
    parser_dir = subparsers.add_parser("directory", help="Annuaire des Services Publics & Monitoring Santé")
    parser_dir.add_argument("--search", help="Recherche textuelle par mot-clé")
    parser_dir.add_argument("--category", help="Filtrer par catégorie")
    parser_dir.add_argument("--eservices", action="store_true", help="Afficher uniquement les démarches en ligne (e-Services)")
    parser_dir.add_argument("--categories", action="store_true", help="Lister toutes les catégories disponibles")
    parser_dir.add_argument("--health", help="Tester la disponibilité en direct d'un portail (ID ou URL)")
    parser_dir.add_argument("--limit", type=int, default=20, help="Nombre max de résultats (défaut: 20)")

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

    elif args.service == "directory":
        handle_directory_command(args)


if __name__ == "__main__":
    main()
