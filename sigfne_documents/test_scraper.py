"""
sigfne_documents/test_scraper.py

Tests unitaires et d'intégration pour le scraper et téléchargeur de documents SIGFNE.
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

from sigfne_documents.scraper import (
    clean_student_code,
    normalize_annee,
    download_sigfne_document,
    get_sigfne_document,
)
import getters


SAMPLE_ERROR_HTML_NO_PAYMENT = """
<!DOCTYPE html>
<html>
<body>
    <form action="/vas/interface-edition-documents-sigfne/" method="POST">
        <div class="form-group">
            <span style="color:red;">Aucun paiement trouvé pour ce matricule (En cas de paiement réussi, s’adresser à l’opérateur svp)</span>
        </div>
    </form>
</body>
</html>
"""

SAMPLE_ERROR_HTML_ACCESS_DENIED = """
<!DOCTYPE html>
<html>
<body>
    <form action="/vas/interface-edition-documents-sigfne/" method="POST">
        <div class="form-group">
            <span style="color:red;">Acces refuse dans votre profil</span>
        </div>
    </form>
</body>
</html>
"""


class TestCleanStudentCode(unittest.TestCase):
    def test_clean_code(self):
        self.assertEqual(clean_student_code(" 12345678a "), "12345678A")
        self.assertEqual(clean_student_code("12345678A"), "12345678A")


class TestNormalizeAnnee(unittest.TestCase):
    def test_direct_code(self):
        self.assertEqual(normalize_annee("2627"), "2627")
        self.assertEqual(normalize_annee("2526"), "2526")

    def test_hyphen_format(self):
        self.assertEqual(normalize_annee("2026-2027"), "2627")
        self.assertEqual(normalize_annee("2025/2026"), "2526")

    def test_fallback(self):
        self.assertEqual(normalize_annee("invalid"), "2627")


class TestDownloadSigfneDocument(unittest.TestCase):
    @patch("sigfne_documents.scraper.Session")
    def test_download_pdf_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"%PDF-1.4 Mock SIGFNE Document Content"
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_session.post.return_value = mock_response

        test_dir = os.path.join(BASE_DIR, "scratch", "test_sigfne_dl")
        res = download_sigfne_document(
            "12345678A",
            doc_type="recu",
            annee="2627",
            output_dir=test_dir,
            session=mock_session,
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["matricule"], "12345678A")
        self.assertEqual(res["doc_type"], "recu")
        self.assertTrue(os.path.exists(res["file_path"]))

        # Nettoyage
        if os.path.exists(res["file_path"]):
            os.remove(res["file_path"])
        if os.path.exists(test_dir):
            os.rmdir(test_dir)

    @patch("sigfne_documents.scraper.Session")
    def test_download_no_payment(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = SAMPLE_ERROR_HTML_NO_PAYMENT.encode("utf-8")
        mock_response.text = SAMPLE_ERROR_HTML_NO_PAYMENT
        mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
        mock_session.post.return_value = mock_response

        res = download_sigfne_document(
            "12345678A",
            doc_type="recu",
            annee="2627",
            session=mock_session,
        )
        self.assertEqual(res["status"], "not_found")
        self.assertIn("Aucun paiement", res["message"])

    @patch("sigfne_documents.scraper.Session")
    def test_download_access_refused(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = SAMPLE_ERROR_HTML_ACCESS_DENIED.encode("utf-8")
        mock_response.text = SAMPLE_ERROR_HTML_ACCESS_DENIED
        mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
        mock_session.post.return_value = mock_response

        res = download_sigfne_document(
            "12345678A",
            doc_type="cursus",
            annee="2627",
            session=mock_session,
        )
        self.assertEqual(res["status"], "not_found")
        self.assertIn("Acces refuse", res["message"])

    def test_invalid_doc_type(self):
        res = download_sigfne_document("12345678A", doc_type="invalid_doc_type")
        self.assertEqual(res["status"], "error")

    def test_empty_matricule(self):
        res = download_sigfne_document("")
        self.assertEqual(res["status"], "error")


class TestGettersSigfneIntegration(unittest.TestCase):
    @patch("sigfne_documents.scraper.download_sigfne_document")
    def test_getters_get_sigfne_document(self, mock_fn):
        mock_fn.return_value = {"status": "success", "file_path": "test.pdf"}
        res = getters.get_sigfne_document("12345678A", doc_type="recu", annee="2627")
        self.assertEqual(res["status"], "success")

    @patch("sigfne_documents.scraper.download_sigfne_document")
    def test_getters_download_sigfne_document(self, mock_fn):
        mock_fn.return_value = {"status": "success", "file_path": "test.pdf"}
        res = getters.download_sigfne_document("12345678A", doc_type="recu", annee="2627")
        self.assertEqual(res["status"], "success")


if __name__ == "__main__":
    unittest.main(verbosity=2)
