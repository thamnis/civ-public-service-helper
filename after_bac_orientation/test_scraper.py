"""
after_bac_orientation/test_scraper.py

Tests unitaires et d'intégration pour le module after_bac_orientation.
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

from after_bac_orientation.scraper import (
    get_bac_orientation_concours,
    get_bac_orientation_concours_admissibles,
    check_bac_orientation_payment,
    simulate_bac_orientation,
)
import getters


SAMPLE_CONCOURS_HTML = """
<!DOCTYPE html>
<html>
<body>
    <div>
        <a href="/orientation/concours/20693">LICENCE ARCHITECTURE Admissibles Consulter</a>
        <a href="/orientation/concours/20695">LICENCE URBANISME Admissibles Consulter</a>
    </div>
</body>
</html>
"""

SAMPLE_ADMISSIBLES_HTML = """
<!DOCTYPE html>
<html>
<body>
    <h1>LICENCE ARCHITECTURE</h1>
    <table>
        <tr><th>N°</th><th>Nom et prénoms</th></tr>
        <tr><td>1</td><td>DOE JANE</td></tr>
        <tr><td>2</td><td>DOE JOHN</td></tr>
    </table>
</body>
</html>
"""

SAMPLE_PAYMENT_NOT_FOUND = """
<!DOCTYPE html>
<html>
<body>
    <div class="alert alert-danger">
        Désole , aucun bachelier trouvé. Veuillez entrer un matricule valide.
    </div>
</body>
</html>
"""


class TestBacOrientationConcours(unittest.TestCase):
    @patch("after_bac_orientation.scraper.Session")
    def test_get_concours(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_CONCOURS_HTML
        mock_session.get.return_value = mock_response

        res = get_bac_orientation_concours(session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["count"], 2)
        self.assertEqual(res["concours"][0]["id"], "20693")

    @patch("after_bac_orientation.scraper.Session")
    def test_get_admissibles(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_ADMISSIBLES_HTML
        mock_session.get.return_value = mock_response

        res = get_bac_orientation_concours_admissibles("20693", session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["count"], 2)
        self.assertEqual(res["admissibles"][0]["nom_prenoms"], "DOE JANE")
        self.assertEqual(res["admissibles"][0]["rang"], 1)

    def test_empty_concours_id(self):
        res = get_bac_orientation_concours_admissibles("")
        self.assertEqual(res["status"], "error")


class TestBacOrientationPaymentAndSimulator(unittest.TestCase):
    @patch("after_bac_orientation.scraper.Session")
    def test_payment_not_found(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_PAYMENT_NOT_FOUND
        mock_session.post.return_value = mock_response

        res = check_bac_orientation_payment("12345678A", session=mock_session)
        self.assertEqual(res["status"], "not_found")
        self.assertFalse(res["is_paid"])

    def test_empty_matricule(self):
        self.assertEqual(check_bac_orientation_payment("")["status"], "error")
        self.assertEqual(simulate_bac_orientation("")["status"], "error")


class TestGettersAfterBacIntegration(unittest.TestCase):
    @patch("after_bac_orientation.scraper.get_bac_orientation_concours")
    def test_getters_concours(self, mock_fn):
        mock_fn.return_value = {"status": "success", "count": 3}
        res = getters.get_bac_orientation_concours()
        self.assertEqual(res["status"], "success")

    @patch("after_bac_orientation.scraper.check_bac_orientation_payment")
    def test_getters_payment(self, mock_fn):
        mock_fn.return_value = {"status": "success", "is_paid": True}
        res = getters.check_bac_orientation_payment("12345678A")
        self.assertEqual(res["status"], "success")


if __name__ == "__main__":
    unittest.main(verbosity=2)
