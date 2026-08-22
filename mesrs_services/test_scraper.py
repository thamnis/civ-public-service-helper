"""
mesrs_services/test_scraper.py

Tests unitaires et d'intégration pour le module mesrs_services.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Configuration de l'encodage de sortie pour Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from mesrs_services.scraper import (
    verify_mesrs_payment,
    get_mesrs_dexco_services,
    get_mesrs_announcements,
)
import getters


SAMPLE_PAYMENT_NOT_FOUND_HTML = """
<!DOCTYPE html>
<html>
<body>
    <div class="alert alert-danger">
        Désolé, la référence de paiement n'existe pas.
    </div>
</body>
</html>
"""

SAMPLE_PAYMENT_SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<body>
    <div class="alert alert-success">
        Paiement validé avec succès.
    </div>
    <table>
        <tr><th>Montant:</th><td>30 000 FCFA</td></tr>
        <tr><th>Établissement:</th><td>Université Félix Houphouët-Boigny</td></tr>
    </table>
</body>
</html>
"""

SAMPLE_DEXCO_HTML = """
<!DOCTYPE html>
<html>
<body>
    <input name="csrf_token" value="test_token_123" />
    <form action="/dexco/choix" method="POST">
        <input name="type_demande" value="dexco_dmd_auth_diplome" />
    </form>
    <form action="/dexco/choix" method="POST">
        <input name="type_demande" value="dexco_dmd_edition_releve_bts" />
    </form>
</body>
</html>
"""

SAMPLE_TICKER_HTML = """
<!DOCTYPE html>
<html>
<body>
    <div class="mesrs-ticker">
        <span class="ticker-item">Test d'intégration en Sciences Médicales session 2026</span>
    </div>
</body>
</html>
"""


class TestVerifyMesrsPayment(unittest.TestCase):
    @patch("mesrs_services.scraper.Session")
    def test_payment_not_found(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_PAYMENT_NOT_FOUND_HTML
        mock_session.post.return_value = mock_response

        res = verify_mesrs_payment(
            "AAAB19920001",
            "1502168548958751",
            "0102030405",
            session=mock_session,
        )
        self.assertEqual(res["status"], "not_found")
        self.assertFalse(res["is_valid"])
        self.assertIn("n'existe pas", res["message"])

    @patch("mesrs_services.scraper.Session")
    def test_payment_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_PAYMENT_SUCCESS_HTML
        mock_session.post.return_value = mock_response

        res = verify_mesrs_payment(
            "AAAB19920001",
            "1502168548958751",
            "0102030405",
            session=mock_session,
        )
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["montant"], "30 000 FCFA")

    def test_empty_parameters(self):
        self.assertEqual(verify_mesrs_payment("", "123", "456")["status"], "error")
        self.assertEqual(verify_mesrs_payment("MAT", "", "456")["status"], "error")
        self.assertEqual(verify_mesrs_payment("MAT", "123", "")["status"], "error")


class TestDexcoAndAnnouncements(unittest.TestCase):
    @patch("mesrs_services.scraper.Session")
    def test_dexco_services(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_DEXCO_HTML
        mock_session.get.return_value = mock_response

        res = get_mesrs_dexco_services(session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["csrf_token"], "test_token_123")
        self.assertEqual(res["count"], 2)
        self.assertEqual(res["services"][0]["code"], "dexco_dmd_auth_diplome")

    @patch("mesrs_services.scraper.Session")
    def test_announcements(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_TICKER_HTML
        mock_session.get.return_value = mock_response

        res = get_mesrs_announcements(session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertTrue(any("Sciences Médicales" in a for a in res["announcements"]))


class TestGettersMesrsIntegration(unittest.TestCase):
    @patch("mesrs_services.scraper.verify_mesrs_payment")
    def test_getters_verify_mesrs_payment(self, mock_fn):
        mock_fn.return_value = {"status": "success", "is_valid": True}
        res = getters.verify_mesrs_payment("AAAB19920001", "1502168548958751", "0102030405")
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["is_valid"])

    @patch("mesrs_services.scraper.get_mesrs_dexco_services")
    def test_getters_get_mesrs_dexco_services(self, mock_fn):
        mock_fn.return_value = {"status": "success", "count": 5}
        res = getters.get_mesrs_dexco_services()
        self.assertEqual(res["status"], "success")

    @patch("mesrs_services.scraper.get_mesrs_announcements")
    def test_getters_get_mesrs_announcements(self, mock_fn):
        mock_fn.return_value = {"status": "success", "announcements": ["News 1"]}
        res = getters.get_mesrs_announcements()
        self.assertEqual(res["status"], "success")


if __name__ == "__main__":
    unittest.main(verbosity=2)
