"""
oneci_services module

Ce module fournit des outils pour interagir avec les services de l'Office National de l'État Civil et de l'Identification (ONECI) de Côte d'Ivoire.
"""
from .scraper import (
    check_cni_status,
    find_numero_demande,
)
