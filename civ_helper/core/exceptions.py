"""
civ_helper/core/exceptions.py

Exceptions spécifiques pour le SDK.
"""

class CivHelperError(Exception):
    """Exception de base pour tous les services."""
    pass

class CivOfflineError(CivHelperError):
    """Le service demandé est hors-ligne ou inaccessible."""
    pass

class CivAuthError(CivHelperError):
    """Une erreur d'authentification (ex: Cookie manquant ou expiré)."""
    pass

class CivCaptchaError(CivHelperError):
    """Un captcha a empêché l'accès au service."""
    pass

class CivParseError(CivHelperError):
    """Impossible de lire ou parser la réponse du serveur."""
    pass
