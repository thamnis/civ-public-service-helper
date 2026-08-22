# 📑 Documents Scolaires & Services MESRS

Ce chapitre présente les modules dédiés aux documents scolaires officiels (SIGFNE / DESPS) et aux services numériques ministériels (MESRS).

---

## 1. Documents Scolaires SIGFNE / DESPS (`agfne.sigfne.net`)

Le sous-module [`sigfne_documents/`](../sigfne_documents/README.md) permet de télécharger les documents officiels édités par la DESPS pour les élèves du secondaire.

### Types de documents disponibles
| Code | Libellé |
|---|---|
| `recu` | Reçu officiel de préinscription |
| `cursus` | Fiche de cursus scolaire standard |
| `cursusnew` | Fiche de cursus scolaire (New) |

### Années scolaires supportées
`1920` (2019-2020) jusqu'à `2627` (2026-2027, valeur par défaut).

### Exemple Python
```python
from getters import download_sigfne_document

# Télécharger le reçu de préinscription
res = download_sigfne_document("12345678A", doc_type="recu", annee="2627")
if res["status"] == "success":
    print("Fichier :", res["file_path"])
    print("Taille  :", res["file_size"], "octets")

# Télécharger une fiche de cursus
res_cursus = download_sigfne_document("12345678A", doc_type="cursus", annee="2526")
print(res_cursus)
```

### Utilisation CLI
```bash
# Reçu de préinscription
python sigfne_documents/main.py --id 12345678A --type recu --annee 2627

# Fiche de cursus
python sigfne_documents/main.py --id 12345678A --type cursus --annee 2526
```

---

## 2. Portail des Services & Inscriptions MESRS (`inscription.mesrs-ci.net`)

Le sous-module [`mesrs_services/`](../mesrs_services/README.md) interagit avec le portail officiel de l'enseignement supérieur.

### Fonctionnalités
- 💳 **Vérification de paiement étudiant** : Contrôle de la validité d'une transaction de paiement d'inscription / réinscription universitaire publique.
- 📑 **Catalogue DEXCO** : Listing des actes d'examen et diplômes disponibles en ligne (authentifications de diplômes, diplômes définitifs BTS, relevés de notes, attestations administratives et d'admissibilité).
- 📢 **Annonces & Tickers Flash** : Récupération des communiqués officiels en temps réel (concours, tests d'intégration Sciences Médicales, ouvertures de plateformes).

### Exemple Python
```python
from getters import verify_mesrs_payment, get_mesrs_dexco_services, get_mesrs_announcements

# Vérification de paiement
res = verify_mesrs_payment("AAAB19920001", "1502168548958751", "0102030405")
if res["status"] == "success" and res["is_valid"]:
    print("Paiement validé avec succès !")

# Catalogue DEXCO
dexco = get_mesrs_dexco_services()
for service in dexco.get("services", []):
    print(f"• [{service['code']}] {service['label']}")

# Annonces flash
news = get_mesrs_announcements()
for item in news.get("announcements", []):
    print("📢", item)
```

### Utilisation CLI
```bash
# Vérifier un paiement
python mesrs_services/main.py --matricule AAAB19920001 --code-paiement 1502168548958751 --numero-paiement 0102030405

# Afficher les actes DEXCO
python mesrs_services/main.py --dexco

# Afficher les annonces officielles
python mesrs_services/main.py --announcements
```
