"""
sixieme_affectation/test_scraper.py

Tests unitaires et d'intégration pour le scraper et téléchargeur d'affectation en 6ème.
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

from sixieme_affectation.scraper import (
    clean_student_code,
    get_student_info,
    get_school_info,
    get_student_school_id,
    download_assignment_document,
    extract_pdf_info,
    get_sixieme_affectation,
)
import getters


SAMPLE_STUDENT_AJAX_OK = {
    "status": "ok",
    "answer": {
        "id": "100001",
        "student_code": "12345678A",
        "student_first_name": "JANE",
        "student_last_name": "DOE",
        "student_age": "12",
        "student_nationality": "Ivoirienne",
        "student_birthday": "01/01/2014",
        "student_gender": "F",
        "student_tgp": "110.00",
    },
}

SAMPLE_SCHOOL_AJAX_OK = {
    "status": "ok",
    "answer": {
        "id": "101",
        "school_name": "LYCEE MODERNE D'EXEMPLE ABIDJAN",
        "school_quartier": "COCODY CENTRE",
        "school_capacity": "200",
        "school_assigned": "150",
        "school_free_place": "50",
        "school_type": "Public",
        "school_gender": "Mixte",
        "school_nationality": "A",
        "school_cost": "0.00",
        "school_comment": "",
    },
}

SAMPLE_SCHOOLID_AJAX_OK = {
    "status": "ok",
    "answer": {
        "schoolid": "101",
        "statusid": "1",
        "type": "GSM",
    },
}

SAMPLE_NOT_FOUND_AJAX = {
    "status": "error",
    "error": "Matricule non trouvé.",
}


class TestCleanStudentCode(unittest.TestCase):
    def test_clean_student_code(self):
        self.assertEqual(clean_student_code(" 12345678a "), "12345678A")
        self.assertEqual(clean_student_code("12345678A"), "12345678A")


class TestGetStudentInfo(unittest.TestCase):
    @patch("sixieme_affectation.scraper.Session")
    def test_student_info_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_STUDENT_AJAX_OK
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response

        res = get_student_info("12345678A", session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["student_code"], "12345678A")
        self.assertEqual(res["first_name"], "JANE")
        self.assertEqual(res["last_name"], "DOE")
        self.assertEqual(res["full_name"], "DOE JANE")
        self.assertEqual(res["birthday"], "01/01/2014")
        self.assertEqual(res["tgp"], "110.00")

    @patch("sixieme_affectation.scraper.Session")
    def test_student_info_not_found(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_NOT_FOUND_AJAX
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response

        res = get_student_info("UNKNOWN000", session=mock_session)
        self.assertEqual(res["status"], "not_found")

    def test_student_info_empty(self):
        res = get_student_info("")
        self.assertEqual(res["status"], "error")


class TestGetSchoolInfo(unittest.TestCase):
    @patch("sixieme_affectation.scraper.Session")
    def test_school_info_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_SCHOOL_AJAX_OK
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response

        res = get_school_info(101, "12345678A", session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["school_name"], "LYCEE MODERNE D'EXEMPLE ABIDJAN")
        self.assertEqual(res["school_cost"], "0.00")
        self.assertEqual(res["school_type"], "Public")


class TestGetStudentSchoolId(unittest.TestCase):
    @patch("sixieme_affectation.scraper.Session")
    def test_school_id_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_SCHOOLID_AJAX_OK
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response

        school_id = get_student_school_id("12345678A", session=mock_session)
        self.assertEqual(school_id, 101)


class TestDownloadAssignmentDocument(unittest.TestCase):
    @patch("sixieme_affectation.scraper.Session")
    def test_download_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.content = b"%PDF-1.4 Mock PDF Content"
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response

        test_dir = os.path.join(BASE_DIR, "scratch", "test_dl")
        res = download_assignment_document("12345678A", output_dir=test_dir, session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertTrue(os.path.exists(res["file_path"]))

        # Nettoyage
        if os.path.exists(res["file_path"]):
            os.remove(res["file_path"])
        if os.path.exists(test_dir):
            os.rmdir(test_dir)


class TestGetSixiemeAffectation(unittest.TestCase):
    @patch("sixieme_affectation.scraper.get_student_info")
    @patch("sixieme_affectation.scraper.get_student_school_id")
    @patch("sixieme_affectation.scraper.get_school_info")
    def test_unified_affectation_pipeline(self, mock_school, mock_school_id, mock_student):
        mock_student.return_value = {
            "status": "success",
            "student_code": "12345678A",
            "full_name": "DOE JANE",
        }
        mock_school_id.return_value = 101
        mock_school.return_value = {
            "status": "success",
            "school_name": "LYCEE MODERNE D'EXEMPLE ABIDJAN",
        }

        res = get_sixieme_affectation("12345678A", download_pdf=False)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["is_assigned"])
        self.assertEqual(res["student"]["full_name"], "DOE JANE")
        self.assertEqual(res["school"]["school_name"], "LYCEE MODERNE D'EXEMPLE ABIDJAN")


class TestGettersModuleIntegration(unittest.TestCase):
    @patch("sixieme_affectation.scraper.get_sixieme_affectation")
    def test_getters_get_sixieme_affectation(self, mock_fn):
        mock_fn.return_value = {"status": "success", "is_assigned": True}
        res = getters.get_sixieme_affectation("12345678A")
        self.assertEqual(res["status"], "success")

    @patch("sixieme_affectation.scraper.get_sixieme_affectation")
    def test_getters_get_result_sixieme_dispatch(self, mock_fn):
        mock_fn.return_value = {"status": "success", "is_assigned": True}
        res = getters.get_result("12345678A", exam="affectation_sixieme")
        self.assertEqual(res["status"], "success")


if __name__ == "__main__":
    unittest.main(verbosity=2)
