"""
infas_convocation/test_scraper.py

Tests unitaires et d'intégration pour le scraper et téléchargeur de convocations INFAS.
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

from infas_convocation.scraper import (
    clean_candidate_code,
    get_csrf_token,
    parse_convocation_view,
    get_infas_convocation_info,
    download_infas_convocation,
    get_infas_convocation,
)
import getters


SAMPLE_PAGE_HTML = """
<!doctype html>
<html>
<body>
    <form action="https://infas.ciconcours.com/listConvocation" method="POST">
        <input type="hidden" name="_token" value="MOCK_CSRF_TOKEN_12345" />
        <input type="text" name="code" />
    </form>
</body>
</html>
"""

SAMPLE_VIEW_HTML_OK = """
<div class="my-3 p-3 bg-body">
    <div id="information">
        <div class="row">
            <div class="col-md-2">
                <img id="imgCandidat" class="img img-thumbnail" src="https://infas.ciconcours.com/storage/photos/CD00000000.jpg" />
            </div>
            <div class="col-md-10">
                <dl class="row">
                    <dt class="col-sm-3">Numéro Candidat</dt>
                    <dd class="col-sm-9">: <b class="text-success">CD00000000</b></dd>
                </dl>
                <dl class="row">
                    <dt class="col-sm-3">Numéro de table</dt>
                    <dd class="col-sm-9">: <b class="text-success">10000001</b></dd>
                </dl>
                <dl class="row">
                    <dt class="col-sm-3">Nom et prénom (s)</dt>
                    <dd class="col-sm-9">: M. DOE JOHN</dd>
                </dl>
                <dl class="row">
                    <dt class="col-sm-3">Date et lieu de naissance</dt>
                    <dd class="col-sm-9">: 01-01-2000 à ABIDJAN</dd>
                </dl>
                <dl class="row">
                    <dt class="col-sm-3">Pièce d'identité</dt>
                    <dd class="col-sm-9">: CNI / C0000000000</dd>
                </dl>
            </div>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Concours</th>
                    <th>Centre</th>
                    <th>Salle</th>
                    <th>Date</th>
                    <th>Heure</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>INFIRMIERS ET INFIRMIERES</td>
                    <td>LYCEE D'EXEMPLE ABIDJAN</td>
                    <td>SALLE 01</td>
                    <td>20 Août 2026</td>
                    <td>08:00:00 - 12:00:00</td>
                </tr>
                <tr>
                    <td colspan="5">
                        <a href="https://infas.ciconcours.com/imprimerConvocation/10000001/CONVOCATION">Imprimer la convocation</a>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
"""


class TestCleanCandidateCode(unittest.TestCase):
    def test_clean_code(self):
        self.assertEqual(clean_candidate_code(" cd00000000 "), "CD00000000")
        self.assertEqual(clean_candidate_code("CD00000000"), "CD00000000")


class TestParseConvocationView(unittest.TestCase):
    def test_parse_success(self):
        res = parse_convocation_view(SAMPLE_VIEW_HTML_OK)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["candidate_id"], "CD00000000")
        self.assertEqual(res["table_number"], "10000001")
        self.assertEqual(res["full_name"], "DOE JOHN")
        self.assertEqual(res["birthdate"], "01-01-2000")
        self.assertEqual(res["birthplace"], "ABIDJAN")
        self.assertEqual(res["id_card"], "CNI / C0000000000")
        self.assertEqual(len(res["sessions"]), 1)
        self.assertEqual(res["sessions"][0]["centre"], "LYCEE D'EXEMPLE ABIDJAN")
        self.assertIn("imprimerConvocation", res["convocation_url"])


class TestGetCsrfToken(unittest.TestCase):
    @patch("infas_convocation.scraper.Session")
    def test_csrf_token_extracted(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_PAGE_HTML
        mock_session.get.return_value = mock_response

        token = get_csrf_token(mock_session)
        self.assertEqual(token, "MOCK_CSRF_TOKEN_12345")


class TestGetInfasConvocationInfo(unittest.TestCase):
    @patch("infas_convocation.scraper.get_csrf_token")
    @patch("infas_convocation.scraper.Session")
    def test_get_info_success(self, mock_session_cls, mock_csrf):
        mock_csrf.return_value = "MOCK_TOKEN"
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"view": SAMPLE_VIEW_HTML_OK}
        mock_session.post.return_value = mock_response

        res = get_infas_convocation_info("CD00000000", session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["full_name"], "DOE JOHN")
        self.assertEqual(res["table_number"], "10000001")

    @patch("infas_convocation.scraper.get_csrf_token")
    @patch("infas_convocation.scraper.Session")
    def test_get_info_not_found(self, mock_session_cls, mock_csrf):
        mock_csrf.return_value = "MOCK_TOKEN"
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_session.post.return_value = mock_response

        res = get_infas_convocation_info("INVALID_CODE", session=mock_session)
        self.assertEqual(res["status"], "not_found")

    def test_empty_candidate_code(self):
        res = get_infas_convocation_info("")
        self.assertEqual(res["status"], "error")


class TestDownloadInfasConvocation(unittest.TestCase):
    @patch("infas_convocation.scraper.get_infas_convocation_info")
    @patch("infas_convocation.scraper.Session")
    def test_download_success(self, mock_session_cls, mock_info):
        mock_info.return_value = {
            "status": "success",
            "candidate_id": "CD00000000",
            "table_number": "10000001",
            "convocation_url": "https://infas.ciconcours.com/imprimerConvocation/10000001/CONVOCATION",
        }
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"%PDF-1.4 Mock PDF Content"
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_session.get.return_value = mock_response

        test_dir = os.path.join(BASE_DIR, "scratch", "test_infas_dl")
        res = download_infas_convocation("CD00000000", output_dir=test_dir, session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertTrue(os.path.exists(res["file_path"]))

        # Nettoyage
        if os.path.exists(res["file_path"]):
            os.remove(res["file_path"])
        if os.path.exists(test_dir):
            os.rmdir(test_dir)


class TestGettersInfasIntegration(unittest.TestCase):
    @patch("infas_convocation.scraper.get_infas_convocation")
    def test_getters_get_infas_convocation(self, mock_fn):
        mock_fn.return_value = {"status": "success", "candidate_id": "CD00000000"}
        res = getters.get_infas_convocation("CD00000000")
        self.assertEqual(res["status"], "success")

    @patch("infas_convocation.scraper.download_infas_convocation")
    def test_getters_download_infas_convocation(self, mock_fn):
        mock_fn.return_value = {"status": "success", "file_path": "test.pdf"}
        res = getters.download_infas_convocation("CD00000000")
        self.assertEqual(res["status"], "success")


if __name__ == "__main__":
    unittest.main(verbosity=2)
