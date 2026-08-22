"""
seconde_orientation/test_scraper.py

Tests unitaires et d'intégration pour le scraper et téléchargeur d'orientation en seconde.
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

from seconde_orientation.scraper import (
    clean_student_code,
    get_student_info,
    get_school_info,
    get_student_school_id,
    download_orientation_document,
    get_seconde_orientation,
)
import getters


SAMPLE_STUDENT_AJAX_OK = {
    "status": "ok",
    "answer": {
        "id": "200001",
        "student_code": "12345678A",
        "student_first_name": "JANE",
        "student_last_name": "DOE",
        "student_age": "15",
        "student_nationality": "Ivoirienne",
        "student_birthday": "01/01/2011",
        "student_gender": "F",
        "student_tgp": "140.50",
        "student_msno": "14.25",
    },
}

SAMPLE_SCHOOL_AJAX_OK = {
    "status": "ok",
    "answer": {
        "id": "501",
        "school_name": "LYCEE CLASSIQUE D'ABIDJAN",
        "school_serie": "2nde C",
        "school_quartier": "COCODY",
        "school_capacity": "300",
        "school_assigned": "280",
        "school_free_place": "20",
        "school_type": "Public",
        "school_gender": "Mixte",
        "school_cost": "0.00",
        "school_comment": "",
    },
}

SAMPLE_SCHOOLID_AJAX_OK = {
    "status": "ok",
    "answer": {
        "schoolid": "501",
        "statusid": "1",
    },
}

SAMPLE_NOT_ORIENTED_AJAX = {
    "status": "error",
    "error": "Elève non orienté à l'enseignement général",
    "answer": None,
}


class TestCleanStudentCode(unittest.TestCase):
    def test_clean_code(self):
        self.assertEqual(clean_student_code(" 12345678a "), "12345678A")
        self.assertEqual(clean_student_code("12345678A"), "12345678A")


class TestGetStudentInfo(unittest.TestCase):
    @patch("seconde_orientation.scraper.Session")
    def test_student_info_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_STUDENT_AJAX_OK
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response

        res = get_student_info("12345678A", session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["student_code"], "12345678A")
        self.assertEqual(res["full_name"], "DOE JANE")
        self.assertEqual(res["msno"], "14.25")

    @patch("seconde_orientation.scraper.Session")
    def test_student_info_not_oriented(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_NOT_ORIENTED_AJAX
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response

        res = get_student_info("12345678A", session=mock_session)
        self.assertEqual(res["status"], "not_found")
        self.assertIn("non orienté", res["message"])

    def test_empty_student_code(self):
        res = get_student_info("")
        self.assertEqual(res["status"], "error")


class TestGetSchoolInfo(unittest.TestCase):
    @patch("seconde_orientation.scraper.Session")
    def test_school_info_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_SCHOOL_AJAX_OK
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response

        res = get_school_info(501, "12345678A", session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["school_name"], "LYCEE CLASSIQUE D'ABIDJAN")
        self.assertEqual(res["serie"], "2nde C")


class TestGetStudentSchoolId(unittest.TestCase):
    @patch("seconde_orientation.scraper.Session")
    def test_school_id_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_SCHOOLID_AJAX_OK
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response

        school_id = get_student_school_id("12345678A", session=mock_session)
        self.assertEqual(school_id, 501)


class TestDownloadOrientationDocument(unittest.TestCase):
    @patch("seconde_orientation.scraper.Session")
    def test_download_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.content = b"%PDF-1.4 Mock Orientation PDF Content"
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response

        test_dir = os.path.join(BASE_DIR, "scratch", "test_seconde_dl")
        res = download_orientation_document("12345678A", output_dir=test_dir, session=mock_session)
        self.assertEqual(res["status"], "success")
        self.assertTrue(os.path.exists(res["file_path"]))

        # Nettoyage
        if os.path.exists(res["file_path"]):
            os.remove(res["file_path"])
        if os.path.exists(test_dir):
            os.rmdir(test_dir)


class TestGetSecondeOrientation(unittest.TestCase):
    @patch("seconde_orientation.scraper.get_student_info")
    @patch("seconde_orientation.scraper.get_student_school_id")
    @patch("seconde_orientation.scraper.get_school_info")
    def test_unified_orientation_pipeline(self, mock_school, mock_school_id, mock_student):
        mock_student.return_value = {
            "status": "success",
            "student_code": "12345678A",
            "full_name": "DOE JANE",
        }
        mock_school_id.return_value = 501
        mock_school.return_value = {
            "status": "success",
            "school_name": "LYCEE CLASSIQUE D'ABIDJAN",
            "serie": "2nde C",
        }

        res = get_seconde_orientation("12345678A", download_pdf=False)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["is_oriented"])
        self.assertEqual(res["student"]["full_name"], "DOE JANE")
        self.assertEqual(res["school"]["serie"], "2nde C")


class TestGettersSecondeIntegration(unittest.TestCase):
    @patch("seconde_orientation.scraper.get_seconde_orientation")
    def test_getters_get_seconde_orientation(self, mock_fn):
        mock_fn.return_value = {"status": "success", "is_oriented": True}
        res = getters.get_seconde_orientation("12345678A")
        self.assertEqual(res["status"], "success")

    @patch("seconde_orientation.scraper.get_seconde_orientation")
    def test_getters_get_result_seconde_dispatch(self, mock_fn):
        mock_fn.return_value = {"status": "success", "is_oriented": True}
        res = getters.get_result("12345678A", exam="orientation_seconde")
        self.assertEqual(res["status"], "success")


if __name__ == "__main__":
    unittest.main(verbosity=2)
