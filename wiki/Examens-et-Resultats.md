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
