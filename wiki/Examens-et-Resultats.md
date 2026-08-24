# 🎓 Examens & Résultats

Ce chapitre décrit les méthodes pour consulter les résultats scolaires et d'enseignement supérieur (BAC, BEPC, BTS).

---

## 1. Brevet de Technicien Supérieur (BTS)

Le module [`bts_result/`](../bts_result/README.md) interagit avec le portail officiel du MESRS ([https://bts.mesrs-ci.net](https://bts.mesrs-ci.net)).

### Fonctionnalités
- 🔍 **Résultats d'admissibilité** : Consultation par matricule / identifiant BTS et date de naissance.
- 📅 **Calendrier de la session** : Inscriptions, épreuves, soutenances, délibérations et réclamations.
- 📊 **Statistiques nationales** : Candidats inscrits, centres, filières, taux de réussite.
- 📚 **Répertoire des 33 filières** : 23 industrielles et 10 tertiaires avec sigles officiels.
- 📥 **Téléchargement de convocation** : Téléchargement du PDF de convocation officielle.

### Exemple Python
```python
from getters import get_bts_result, get_bts_calendar, get_bts_statistics, get_bts_filieres

# Consultation candidat
candidat = get_bts_result("DOJO010100001", birthdate="01/01/2000")
if candidat["status"] == "success":
    print("Statut :", "ADMISSIBLE" if candidat["is_admitted"] else "REFUSÉ")
    print("Candidat :", candidat["full_name"])
    print("Filière :", candidat["sector"])

# Calendrier
cal = get_bts_calendar()
for ev in cal.get("events", []):
    print(f"• {ev['etape']} : {ev['periode']}")

# Statistiques
stats = get_bts_statistics()
print("Taux de réussite :", stats["statistics"].get("taux_reussite"))
```

### Utilisation CLI
```bash
# Consulter un candidat
python bts_result/main.py --id DOJO010100001 --birthdate 01/01/2000

# Afficher le calendrier officiel
python bts_result/main.py --calendar

# Afficher les statistiques nationales
python bts_result/main.py --stats

# Télécharger la convocation
python bts_result/main.py --id DOJO010100001 --convocation
```

---

## 2. Baccalauréat (BAC) et Brevet d'Études du Premier Cycle (BEPC)

La consultation des résultats du BAC et du BEPC s'effectue via la passerelle DECO ([https://itdeco.ci](https://itdeco.ci)).

### Exemple Python
```python
from getters import get_result

# Résultat BAC
res_bac = get_result("12345678A", exam="bac")
print(res_bac)

# Résultat BEPC
res_bepc = get_result("12345678A", exam="bepc")
print(res_bepc)
```

---

## 3. Examens Professionnels & Enseignement Technique — DEXC METFPA (`dexc.ci`)

La **Direction des Examens et Concours (DEXC)** du Ministère de l'Enseignement Technique, de la Formation Professionnelle et de l'Apprentissage (METFPA) gère l'organisation, les jurys et les délibérations des diplômes techniques d'État (CAP, BT, BP, BEP, CQP) via la plateforme **SYGADEXC** ([http://dexc.ci](http://dexc.ci)).

### Missions & Fonctionnalités de la plateforme `dexc.ci`
- 📋 **Gestion des Examens et Diplômes Techniques** :
  - **CAP** : Certificat d'Aptitude Professionnelle
  - **BT** : Brevet de Technicien
  - **BP** : Brevet Professionnel
  - **BEP** : Brevet d'Études Professionnelles
  - **CQP** : Certificat de Qualification Professionnelle
- ✍️ **Espace Acteurs & Correcteurs** (`/espace-acteur`, `/inscription-acteur-correcteur`) :
  - Inscription des examinateurs, correcteurs, présidents et vice-présidents de jury (PJ/VPJ), superviseurs et membres de secrétariat.
  - Saisie des informations d'identité (CNI) et bancaires (RIB) pour le traitement des indemnités de session.
  - Choix et affectation aux centres de composition et de délibération (`/choix-centres-correcteurs`).
- 🏢 **Espace Directions Régionales (DR)** (`/espace-dr`, `/espace-drdexc`) :
  - Proposition et validation des centres d'examens régionaux (`/validations-centres`).
  - Validation et confirmation des listes d'acteurs de session (`/validations-acteurs`).
- 💰 **Suivi des États de Paiements et Indemnités** :
  - États d'indemnités pour les épreuves écrites (`/axes-ecrit`), épreuves physiques EPS (`/axes-eps`), travaux pratiques TP (`/axes-tp`) et soutenances (`/axes-soutenance`).
  - États de paiement centralisés pour les examens (`/etats-paiements-examens`) et concours professionnels (`/etats-paiements-concours`).

