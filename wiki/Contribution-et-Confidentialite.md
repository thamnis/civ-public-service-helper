# 🛡️ Confidentialité, Tests & Contribution

Ce chapitre décrit les règles de développement, les protocoles de confidentialité et les procédures pour contribuer au projet.

---

## 🔒 1. Règle Fondamentale de Confidentialité

> [!CAUTION]
> **Ne jamais commiter ou versionner de données personnelles réelles** (matricules réels d'élèves, noms réels, dates de naissance réelles, numéros de téléphone réels ou références de paiement privées).

### Bonnes pratiques :
- Utiliser systématiquement des **matricules factices** dans le code, la documentation et les fichiers de test :
  - Scolaire / DOB : `12345678A`, `87654321B`
  - BTS : `DOJO010100001`, `BTS2026000001`
  - INFAS : `CD00000000`, `CA00000000`
  - MESRS : `AAAB19920001`
- Utiliser des noms factices : `DOE Jane`, `DOE John`.
- Utiliser des dates factices : `01/01/2000`, `01/01/2011`.
- Les fichiers `data.json` de chaque module ne doivent contenir que des données d'exemple génériques.
- Vérifier avant tout commit avec `git diff` ou un outil de recherche de motifs.

---

## 🧪 2. Exécution des Tests Unitaires

Le projet dispose d'une suite de 72 tests unitaires couvrant l'ensemble des modules.

### Lancer tous les tests unitaires :
```bash
python -m unittest after_bac_orientation/test_scraper.py mesrs_services/test_scraper.py bts_result/test_scraper.py sigfne_documents/test_scraper.py seconde_orientation/test_scraper.py infas_convocation/test_scraper.py sixieme_affectation/test_scraper.py -v
```

### Lancer les tests d'un sous-module spécifique :
```bash
# Exemple pour le BTS
python -m unittest bts_result/test_scraper.py -v

# Exemple pour INFAS
python -m unittest infas_convocation/test_scraper.py -v
```

---

## 🏗️ 3. Structure Recommandée pour un Nouveau Module

Pour ajouter un nouveau service ou scraper, suivre la structure modulaire établie :

```text
nouveau_service/
├── scraper.py         # Logique d'extraction, requêtes HTTP, parsing HTML/PDF
├── main.py            # Interface CLI (unitaire, options spécifiques, batch)
├── data.json          # Données factices d'exemple
├── test_scraper.py    # Suite de tests unitaires mockés
└── README.md          # Documentation complète du module
```

Puis :
1. Exporter les fonctions de haut niveau dans [`getters.py`](../getters.py).
2. Ajouter le sous-module dans le tableau du [`README.md`](../README.md) principal.
3. Vérifier que tous les tests passent et qu'aucune donnée personnelle n'est présente.
