# 🏛️ Annuaire National & Monitoring des Services Publics Ivoiriens

Le module `civ_helper.services.directory` fournit un accès programmatique, CLI et API au référentiel officiel des services publics, ministères, institutions régaliennes, autorités de régulation et plateformes e-services de Côte d'Ivoire (+100 portails).

Il intègre également un système de test de disponibilité et de temps de réponse en temps réel (**Gov Health Check**).

---

## 📦 Utilisation via le SDK Python

```python
from civ_helper.services import directory

# 1. Recherche par mot-clé (insensible à la casse et aux accents)
res = directory.get_services(query="impots")
print(f"Trouvé: {res['total']} services")
for s in res["services"]:
    print(f"• {s['name']} -> {s['url']}")

# 2. Filtrer les démarches et e-services dématérialisés
e_services = directory.get_e_services(limit=10)
for es in e_services:
    print(f"⚡ [{es['name']}] : {es['url']}")

# 3. Lister toutes les catégories disponibles
categories = directory.get_categories()
for cat in categories:
    print(f"📂 {cat['category']} ({cat['count']} services)")

# 4. Tester la disponibilité d'un portail (Health Check / Uptime)
health = directory.check_service_health("https://statut.oneci.ci")
print(health)
# Résultat :
# {
#   "name": "Portail Public",
#   "url": "https://statut.oneci.ci",
#   "status": "online",
#   "status_code": 200,
#   "response_time_ms": 342.15,
#   "message": "En ligne (Code HTTP 200)"
# }
```

---

## 💻 Utilisation via la Ligne de Commande (CLI)

```bash
# Rechercher un service par mot-clé
python -m civ_helper.cli directory --search "foncier"

# Lister les démarches en ligne (e-services)
python -m civ_helper.cli directory --eservices

# Filtrer par catégorie
python -m civ_helper.cli directory --category "Justice"

# Lister les catégories existantes
python -m civ_helper.cli directory --categories

# Tester l'état et la réactivité d'un portail en direct
python -m civ_helper.cli directory --health "https://e-justice.ci"
python -m civ_helper.cli directory --health 1
```

---

## 🌐 Endpoints API REST (FastAPI)

Le backend expose ces fonctionnalités sous le tag **`Annuaire & Santé des Services`** :

| Méthode | Route | Description | Paramètres |
|---|---|---|---|
| `GET` | `/api/v1/directory/services` | Liste et filtre les services | `search`, `category`, `is_eservice`, `limit`, `offset` |
| `GET` | `/api/v1/directory/services/{id}` | Détail d'une institution par son ID | `service_id` |
| `GET` | `/api/v1/directory/categories` | Liste des catégories avec comptage | - |
| `GET` | `/api/v1/directory/e-services` | Liste des démarches en ligne | `limit` |
| `GET` | `/api/v1/directory/health` | Diagnostic de disponibilité en direct | `target` (URL ou ID) |

---

## 📊 Structure des Données (`directory.json`)

Chaque entrée de l'annuaire est modélisée comme suit :
```json
{
  "id": 21,
  "name": "Direction Générale des Impôts - Portail e-impôts",
  "url": "https://www.e-impots.gouv.ci",
  "description": "Service ou portail public facilitant l'accès aux textes, à l'identification, aux formalités administratives...",
  "history": "Lancée dans le cadre de la modernisation fiscale, elle vise à simplifier les démarches...",
  "interest": "Essentielle pour les entreprises et contribuables souhaitant gérer leurs obligations fiscales en ligne.",
  "categories": [
    "Administration fiscale",
    "Services en ligne",
    "Économie"
  ],
  "is_eservice": true
}
```
