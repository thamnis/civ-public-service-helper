# 🇨🇮 Portail des Services & Inscriptions MESRS (`inscription.mesrs-ci.net`)

Ce sous-module permet d'interagir avec le portail officiel des inscriptions et services du **Ministère de l'Enseignement Supérieur et de la Recherche Scientifique (MESRS)** de Côte d'Ivoire ([https://inscription.mesrs-ci.net](https://inscription.mesrs-ci.net)).

---

## 📚 Fonctionnalités

- 💳 **Vérification de paiement** : Vérifier la validité d'une transaction de paiement d'inscription ou de réinscription universitaire publique / grande école (`/verifier/paiement`).
- 📑 **Catalogue DEXCO** : Lister les actes d'examen et diplômes disponibles pour demande en ligne (authentification, diplôme définitif, relevé de notes BTS, attestation administrative, attestation d'admissibilité).
- 📢 **Annonces & Tickers Flash** : Récupérer en temps réel les communiqués officiels, sessions de concours (ex: Test d'intégration en Sciences Médicales) et ouvertures de plateformes.
- ⚡ **Support CLI & batch** à partir de fichiers JSON.

---

## 📁 Structure du module

```text
mesrs_services/
├── scraper.py         # Logique d'interrogation du portail MESRS
├── main.py            # CLI unitaire, informations et traitement par lot
├── data.json          # Fichier de données de test avec valeurs fictives
├── test_scraper.py    # Suite de tests unitaires mockés
└── README.md          # Documentation détaillée du module
```

---

## 🚀 Utilisation en ligne de commande (CLI)

### 1. Vérifier un paiement d'inscription
```bash
python mesrs_services/main.py --matricule AAAB19920001 --code-paiement 1502168548958751 --numero-paiement 0102030405
```

### 2. Lister les actes disponibles via DEXCO
```bash
python mesrs_services/main.py --dexco
```

### 3. Afficher les annonces officielles et flash
```bash
python mesrs_services/main.py --announcements
```

### 4. Traitement par lot à partir d'un fichier JSON
```bash
python mesrs_services/main.py --file mesrs_services/data.json --save-json results.json
```

---

## 🐍 Utilisation en Python

### Exemple 1 : Vérification d'un paiement étudiant
```python
from getters import verify_mesrs_payment

res = verify_mesrs_payment(
    matricule_mesrs="AAAB19920001",
    code_paiement="1502168548958751",
    numero_paiement="0102030405",
)

if res["status"] == "success" and res["is_valid"]:
    print("Paiement validé avec succès !")
else:
    print("Statut :", res["message"])
```

### Exemple 2 : Obtenir le catalogue DEXCO et les annonces
```python
from getters import get_mesrs_dexco_services, get_mesrs_announcements

# Actes DEXCO
dexco = get_mesrs_dexco_services()
for service in dexco.get("services", []):
    print(f"• [{service['code']}] {service['label']}")

# Annonces flash
news = get_mesrs_announcements()
for item in news.get("announcements", []):
    print("📢", item)
```

---

## 📊 Format des données retournées (Exemple fictif)

```json
{
  "status": "success",
  "is_valid": true,
  "matricule_mesrs": "AAAB19920001",
  "code_paiement": "1502168548958751",
  "numero_paiement": "0102030405",
  "montant": "30 000 FCFA",
  "message": "Paiement validé avec succès."
}
```

---

## 🧪 Tests

Pour exécuter les tests unitaires du module :
```bash
python -m unittest mesrs_services/test_scraper.py -v
```
