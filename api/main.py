"""
api/main.py

API REST FastAPI pour civ-public-service-helper.
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from civ_helper.services import deco, cei, mfp, justice, oneci
from civ_helper.core.exceptions import CivHelperError

app = FastAPI(
    title="API Services Publics CI",
    description="API non-officielle pour interroger les services publics de Côte d'Ivoire.",
    version="1.0.0"
)

# Configuration CORS pour autoriser le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def handle_civ_request(func, *args, **kwargs):
    try:
        res = func(*args, **kwargs)
        return res
    except CivHelperError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne du serveur: {str(e)}")


@app.get("/api/v1/deco/bepc/{matricule}")
def get_bepc(matricule: str):
    return handle_civ_request(deco.get_bepc_result, matricule)

@app.get("/api/v1/deco/cepe/{matricule}")
def get_cepe(matricule: str):
    return handle_civ_request(deco.get_cepe_result, matricule)

@app.get("/api/v1/cei/voter/{cni}")
def get_voter(cni: str):
    return handle_civ_request(cei.check_voter_status, cni)

@app.get("/api/v1/mfp/concours/{numero}")
def get_mfp(numero: str):
    return handle_civ_request(mfp.get_concours_result, numero)

@app.get("/api/v1/justice/casier/{demande}")
def get_justice(demande: str, cookie: Optional[str] = Header(None)):
    return handle_civ_request(justice.check_demande_status, demande, session_cookie=cookie or "")


class OneciRequest(BaseModel):
    numero: str
    nom: str
    date_naissance: str
    titre: str = "CNI"
    token: str = ""

@app.post("/api/v1/oneci/status")
def get_oneci(req: OneciRequest):
    return handle_civ_request(
        oneci.check_cni_status, 
        numero_demande=req.numero, 
        nom=req.nom, 
        date_naissance=req.date_naissance, 
        titre=req.titre, 
        recaptcha_token=req.token
    )
