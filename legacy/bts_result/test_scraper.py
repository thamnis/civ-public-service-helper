"""
bts_result/test_scraper.py

Tests unitaires et d'intégration pour le scrapper de résultats BTS.
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

# Ajout du dossier parent et du dossier bts_result au sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from bts_result.scraper import normalize_birthdate, parse_bts_html, get_bts_result
import getters


SAMPLE_ADMISSIBLE_HTML = """
<!DOCTYPE html>
<html>
<body>
    <div class="container">
        <div class="text-center p-4 shadow-lg rounded-4">
            <h2 class="fw-bold text-success mb-3">🎉 Félicitations 🎉</h2>
            <img src="/static/img/success.png" />
            <div class="mb-3 text-muted">
                <span class="fw-bold">BTS2026000001</span> / <span class="fw-bold">TEST0101000001</span>
            </div>
            <h4 class="fw-bold text-dark">
                DOE
                JOHN
            </h4>
            <p class="text-secondary mb-3">
                <b><span>01/01/2000</span></b> à <b>ABIDJAN</b>
            </p>
            <p class="fs-5 fw-bold text-muted">
                IDA/INFORMATIQUE DEVELOPPEUR D'APPLICATIONS
            </p>
            <hr/>
            <p class="admissible-message-premium">
                Vous avez été déclaré <b>admissible</b> au BTS session 2026
            </p>
        </div>
    </div>
</body>
</html>
"""

SAMPLE_NOT_FOUND_HTML = """
<!DOCTYPE html>
<html>
<body>
    <div class="container">
        <div class="alert alert-danger">
            Désolé, l'identifiant / numéro BTS ou la date de naissance est incorrect.
        </div>
    </div>
</body>
</html>
"""


class TestNormalizeBirthdate(unittest.TestCase):
    def test_iso_format(self):
        self.assertEqual(normalize_birthdate("2000-01-16"), "2000-01-16")

    def test_slash_format(self):
        self.assertEqual(normalize_birthdate("16/01/2000"), "2000-01-16")
        self.assertEqual(normalize_birthdate("02/11/2004"), "2004-11-02")

    def test_dash_dmy_format(self):
        self.assertEqual(normalize_birthdate("16-01-2000"), "2000-01-16")

    def test_dot_format(self):
        self.assertEqual(normalize_birthdate("16.01.2000"), "2000-01-16")

    def test_empty_string(self):
        with self.assertRaises(ValueError):
            normalize_birthdate("")


class TestParseBtsHtml(unittest.TestCase):
    def test_parse_admissible_candidate(self):
        result = parse_bts_html(SAMPLE_ADMISSIBLE_HTML)
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["is_admitted"])
        self.assertEqual(result["decision"], "admissible")
        self.assertEqual(result["bts_id"], "BTS2026000001")
        self.assertEqual(result["student_id"], "TEST0101000001")
        self.assertEqual(result["full_name"], "DOE JOHN")
        self.assertEqual(result["last_name"], "DOE")
        self.assertEqual(result["first_name"], "JOHN")
        self.assertEqual(result["birthdate"], "01/01/2000")
        self.assertEqual(result["birthplace"], "ABIDJAN")
        self.assertEqual(result["sector"], "IDA/INFORMATIQUE DEVELOPPEUR D'APPLICATIONS")
        self.assertEqual(result["session"], "2026")
        self.assertIn("admissible", result["message"].lower())

    def test_parse_not_found(self):
        result = parse_bts_html(SAMPLE_NOT_FOUND_HTML)
        self.assertEqual(result["status"], "not_found")
        self.assertFalse(result["is_admitted"])
        self.assertIn("incorrect", result["message"])
        self.assertIsNone(result["data"])

    def test_parse_empty_html(self):
        result = parse_bts_html("<html><body></body></html>")
        self.assertEqual(result["status"], "not_found")
        self.assertFalse(result["is_admitted"])


class TestGetBtsResultMocked(unittest.TestCase):
    @patch("bts_result.scraper.Session")
    def test_mocked_candidate_lookup(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.text = SAMPLE_ADMISSIBLE_HTML
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response
        mock_session_cls.return_value = mock_session

        result = get_bts_result("TEST0101000001", "2000-01-01", session=mock_session)
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["is_admitted"])
        self.assertEqual(result["bts_id"], "BTS2026000001")
        self.assertEqual(result["student_id"], "TEST0101000001")
        self.assertEqual(result["full_name"], "DOE JOHN")
        self.assertEqual(result["birthplace"], "ABIDJAN")

    @patch("bts_result.scraper.Session")
    def test_mocked_invalid_candidate(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.text = SAMPLE_NOT_FOUND_HTML
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response
        mock_session_cls.return_value = mock_session

        result = get_bts_result("INVALID_MATRICULE_XYZ", "2000-01-01", session=mock_session)
        self.assertEqual(result["status"], "not_found")
        self.assertFalse(result["is_admitted"])

    def test_validation_empty_inputs(self):
        r1 = get_bts_result("", "2000-01-01")
        self.assertEqual(r1["status"], "error")
        r2 = get_bts_result("TEST0101000001", "")
        self.assertEqual(r2["status"], "error")


class TestGettersIntegration(unittest.TestCase):
    @patch("bts_result.scraper.get_bts_result")
    def test_getters_get_bts_result(self, mock_get_bts):
        mock_get_bts.return_value = {"status": "success", "is_admitted": True}
        res = getters.get_bts_result("TEST0101000001", "2000-01-01")
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["is_admitted"])

    @patch("bts_result.scraper.get_bts_result")
    def test_getters_get_result_bts_dispatch(self, mock_get_bts):
        mock_get_bts.return_value = {"status": "success", "is_admitted": True}
        res = getters.get_result("TEST0101000001", exam="bts", birthdate="2000-01-01")
        self.assertEqual(res["status"], "success")

    def test_getters_get_result_bts_missing_birthdate(self):
        with self.assertRaises(ValueError):
            getters.get_result("TEST0101000001", exam="bts")


class TestBtsUtilities(unittest.TestCase):
    @patch("bts_result.scraper.Session")
    def test_get_bts_calendar_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <table>
            <tr><td>Étape 1</td><td>01 Janvier au 15 Janvier</td></tr>
            <tr><td>Étape 2</td><td>01 Février au 15 Février</td></tr>
        </table>
        """
        mock_session.get.return_value = mock_response

        from bts_result.scraper import get_bts_calendar
        res = get_bts_calendar(session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["count"], 2)
        self.assertEqual(res["events"][0]["etape"], "Étape 1")

    @patch("bts_result.scraper.Session")
    def test_get_bts_statistics_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <div class="bts-stat">
            <div class="value">50 000</div>
            <div class="label">Candidats inscrits</div>
        </div>
        <div class="bts-stat">
            <div class="value">45,50%</div>
            <div class="label">Taux de réussite</div>
        </div>
        """
        mock_session.get.return_value = mock_response

        from bts_result.scraper import get_bts_statistics
        res = get_bts_statistics(session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["statistics"]["candidats_inscrits"], "50 000")
        self.assertEqual(res["statistics"]["taux_reussite"], "45,50%")

    @patch("bts_result.scraper.Session")
    def test_get_bts_filieres_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <div class="card">IDA Informatique developpeur d'applications</div>
        <div class="card">RIT Reseaux informatiques et telecommunications</div>
        """
        mock_session.get.return_value = mock_response

        from bts_result.scraper import get_bts_filieres
        res = get_bts_filieres(category="industrielles", session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["industrielles"]), 2)
        self.assertEqual(res["industrielles"][0]["sigle"], "IDA")


if __name__ == "__main__":
    unittest.main(verbosity=2)
