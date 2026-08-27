"""
api/main.py

API REST FastAPI pour civ-public-service-helper.
Expose tous les services publics ivoiriens (Modernes et Legacy).
"""

from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Nouveaux services refactorisés
from civ_helper.services import deco, cei, mfp, justice, oneci
from civ_helper.core.exceptions import CivHelperError

# Services legacy via getters
import getters

app = FastAPI(
    title="API Services Publics CI",
    description="API centralisée pour interroger les services publics de Côte d'Ivoire (Examens, Pièces d'identité, Concours, etc.).",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def handle_request(func, *args, **kwargs):
    """Wrapper pour intercepter et standardiser les erreurs."""
    try:
        res = func(*args, **kwargs)
        if isinstance(res, dict) and res.get("status") == "error":
            raise HTTPException(status_code=400, detail=res.get("message", "Erreur inconnue"))
        return res
    except CivHelperError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


# ==========================================
# 1. ONECI (Identité)
# ==========================================
class OneciRequest(BaseModel):
    numero: str
    nom: str
    date_naissance: str
    titre: str = "CNI"
    token: str = ""

@app.post("/api/v1/oneci/status", tags=["ONECI"])
def check_oneci_status(req: OneciRequest):
    return handle_request(
        oneci.check_cni_status, 
        numero_demande=req.numero, nom=req.nom, 
        date_naissance=req.date_naissance, titre=req.titre, recaptcha_token=req.token
    )

class OneciFindRequest(BaseModel):
    nom: str
    prenoms: str
    date_naissance: str
    lieu_naissance: str
    titre: str = "CNI"
    token: str = ""

@app.post("/api/v1/oneci/find-numero", tags=["ONECI"])
def find_oneci_numero(req: OneciFindRequest):
    return handle_request(
        oneci.find_numero_demande, 
        nom=req.nom, prenoms=req.prenoms, date_naissance=req.date_naissance,
        lieu_naissance=req.lieu_naissance, titre=req.titre, recaptcha_token=req.token
    )

# ==========================================
# 2. DECO (BEPC / CEPE)
# ==========================================
@app.get("/api/v1/deco/bepc/{matricule}", tags=["DECO"])
def get_bepc(matricule: str):
    return handle_request(deco.get_bepc_result, matricule)

@app.get("/api/v1/deco/cepe/{matricule}", tags=["DECO"])
def get_cepe(matricule: str):
    return handle_request(deco.get_cepe_result, matricule)


# ==========================================
# 3. CEI (Élections)
# ==========================================
@app.get("/api/v1/cei/voter/{cni}", tags=["CEI"])
def get_voter(cni: str):
    return handle_request(cei.check_voter_status, cni)


# ==========================================
# 4. FONCTION PUBLIQUE & JUSTICE
# ==========================================
@app.get("/api/v1/mfp/concours/{numero}", tags=["MFP"])
def get_mfp(numero: str):
    return handle_request(mfp.get_concours_result, numero)

@app.get("/api/v1/justice/casier/{demande}", tags=["Justice"])
def get_justice(demande: str, cookie: Optional[str] = Header(None)):
    return handle_request(justice.check_demande_status, demande, session_cookie=cookie or "")


# ==========================================
# 5. RESULTATS SCOLAIRES (BTS, BAC, 6e, 2nde)
# ==========================================
@app.get("/api/v1/education/bts/resultat/{matricule}", tags=["Enseignement Supérieur (BTS)"])
def get_bts(matricule: str, birthdate: str = Query(..., description="Date de naissance (ex: 2000-01-01)")):
    return handle_request(getters.get_bts_result, matricule, birthdate)

@app.get("/api/v1/education/bts/calendrier", tags=["Enseignement Supérieur (BTS)"])
def bts_calendar():
    return handle_request(getters.get_bts_calendar)

@app.get("/api/v1/education/bts/statistiques", tags=["Enseignement Supérieur (BTS)"])
def bts_stats():
    return handle_request(getters.get_bts_statistics)

@app.get("/api/v1/education/bts/filieres", tags=["Enseignement Supérieur (BTS)"])
def bts_filieres(category: str = "all"):
    return handle_request(getters.get_bts_filieres, category)

@app.get("/api/v1/education/bac/orientation/{matricule}", tags=["Enseignement Supérieur (BAC)"])
def bac_orientation(matricule: str):
    return handle_request(getters.get_bac_orientation_result, matricule)

@app.get("/api/v1/education/bac/simulation/{matricule}", tags=["Enseignement Supérieur (BAC)"])
def bac_simulation(matricule: str):
    return handle_request(getters.simulate_bac_orientation, matricule)

@app.get("/api/v1/education/bac/concours", tags=["Enseignement Supérieur (BAC)"])
def bac_concours():
    return handle_request(getters.get_bac_orientation_concours)

@app.get("/api/v1/education/bac/paiement/{matricule}", tags=["Enseignement Supérieur (BAC)"])
def bac_paiement(matricule: str):
    return handle_request(getters.check_bac_orientation_payment, matricule)

@app.get("/api/v1/education/sixieme/{matricule}", tags=["Affectation Scolaire (DOB)"])
def sixieme_affectation(matricule: str):
    return handle_request(getters.get_sixieme_affectation, matricule, download_pdf=False)

@app.get("/api/v1/education/seconde/{matricule}", tags=["Affectation Scolaire (DOB)"])
def seconde_orientation(matricule: str):
    return handle_request(getters.get_seconde_orientation, matricule, download_pdf=False)


# ==========================================
# 6. CONCOURS INFAS & CAFOP
# ==========================================
@app.get("/api/v1/concours/infas/{numero}", tags=["Concours (INFAS & CAFOP)"])
def infas_convocation(numero: str):
    return handle_request(getters.get_infas_convocation, numero, download_pdf=False)

@app.get("/api/v1/concours/cafop/{matricule}", tags=["Concours (INFAS & CAFOP)"])
def cafop_affectation(matricule: str):
    return handle_request(getters.get_cafop_affectation, matricule)


# ==========================================
# 7. MEN-DELC & MESRS (Annuaires et Actes)
# ==========================================
@app.get("/api/v1/mesrs/paiement/verifier", tags=["MESRS"])
def verifier_paiement_mesrs(matricule: str, code: str, numero: str):
    return handle_request(getters.verify_mesrs_payment, matricule, code, numero)

@app.get("/api/v1/mesrs/dexco", tags=["MESRS"])
def mesrs_dexco():
    return handle_request(getters.get_mesrs_dexco_services)

@app.get("/api/v1/mesrs/annonces", tags=["MESRS"])
def mesrs_annonces():
    return handle_request(getters.get_mesrs_announcements)

@app.get("/api/v1/men-delc/textes-officiels", tags=["MEN-DELC"])
def textes_officiels():
    return handle_request(getters.get_textes_officiels)

@app.get("/api/v1/men-delc/annuaires/drena", tags=["MEN-DELC"])
def drena_directory():
    return handle_request(getters.get_drena_directory)

@app.get("/api/v1/men-delc/annuaires/iepp", tags=["MEN-DELC"])
def iepp_directory():
    return handle_request(getters.get_iepp_directory)


# ==========================================
# 8. ANNUAIRE & MONITORING SANTÉ DES SERVICES
# ==========================================
from civ_helper.services import directory

@app.get("/api/v1/directory/services", tags=["Annuaire & Santé des Services"])
def list_services(
    search: Optional[str] = Query(None, description="Recherche par mot-clé"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    is_eservice: Optional[bool] = Query(None, description="Filtrer uniquement les démarches en ligne"),
    limit: int = Query(50, ge=1, le=200, description="Nombre d'éléments"),
    offset: int = Query(0, ge=0, description="Décalage pagination")
):
    return handle_request(
        directory.get_services,
        query=search,
        category=category,
        is_eservice=is_eservice,
        limit=limit,
        offset=offset
    )

@app.get("/api/v1/directory/services/{service_id}", tags=["Annuaire & Santé des Services"])
def get_service_details(service_id: int):
    svc = directory.get_service_by_id(service_id)
    if not svc:
        raise HTTPException(status_code=404, detail=f"Service ID {service_id} non trouvé")
    return svc

@app.get("/api/v1/directory/categories", tags=["Annuaire & Santé des Services"])
def list_categories():
    return handle_request(directory.get_categories)

@app.get("/api/v1/directory/e-services", tags=["Annuaire & Santé des Services"])
def list_e_services(limit: int = Query(50, ge=1, le=100)):
    return handle_request(directory.get_e_services, limit=limit)

@app.get("/api/v1/directory/health", tags=["Annuaire & Santé des Services"])
def check_portal_health(target: str = Query(..., description="ID du service ou URL du portail")):
    return handle_request(directory.check_service_health, url_or_id=target)

