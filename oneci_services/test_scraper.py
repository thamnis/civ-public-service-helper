"""
oneci_services/test_scraper.py

Tests unitaires pour le module oneci_services.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from oneci_services.scraper import check_cni_status, find_numero_demande


SAMPLE_HTML_CSRF = """
<html><body>
    <input name="csrf_token" type="hidden" value="fake_csrf_token"/>
</body></html>
"""

SAMPLE_HTML_ERROR = """
<html><body>
    <div class="alert alert-danger">Désolé, aucune demande trouvée.</div>
</body></html>
"""

SAMPLE_HTML_SUCCESS = """
<html><body>
    <div class="alert alert-success">Votre carte est prête et disponible.</div>
</body></html>
"""


class TestOneciScraper(unittest.TestCase):
    
    @patch("oneci_services.scraper.Session")
    def test_check_cni_status_error(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response_get = MagicMock()
        mock_response_get.status_code = 200
        mock_response_get.text = SAMPLE_HTML_CSRF
        
        mock_response_post = MagicMock()
        mock_response_post.status_code = 200
        mock_response_post.text = SAMPLE_HTML_ERROR
        
        mock_session.get.return_value = mock_response_get
        mock_session.post.return_value = mock_response_post
        
        res = check_cni_status("1234567890", "DOE", "1990-01-01", session=mock_session)
        self.assertEqual(res["status"], "error")
        self.assertIn("Désolé, aucune demande trouvée", res["message"])
        
    @patch("oneci_services.scraper.Session")
    def test_check_cni_status_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response_get = MagicMock()
        mock_response_get.status_code = 200
        mock_response_get.text = SAMPLE_HTML_CSRF
        
        mock_response_post = MagicMock()
        mock_response_post.status_code = 200
        mock_response_post.text = SAMPLE_HTML_SUCCESS
        
        mock_session.get.return_value = mock_response_get
        mock_session.post.return_value = mock_response_post
        
        res = check_cni_status("1234567890", "DOE", "1990-01-01", session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertIn("Votre carte est prête", res["message"])
        
    @patch("oneci_services.scraper.Session")
    def test_403_forbidden(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response_get = MagicMock()
        mock_response_get.status_code = 200
        mock_response_get.text = SAMPLE_HTML_CSRF
        
        mock_response_post = MagicMock()
        mock_response_post.status_code = 403
        
        mock_session.get.return_value = mock_response_get
        mock_session.post.return_value = mock_response_post
        
        res = check_cni_status("1234567890", "DOE", "1990-01-01", session=mock_session)
        self.assertEqual(res["status"], "error")
        self.assertIn("Accès refusé", res["message"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
