import unittest
from unittest.mock import patch, MagicMock
from cafop_services.scraper import get_cafop_affectation, get_cafop_directors_directory

class TestCafopScraper(unittest.TestCase):
    
    @patch('cafop_services.scraper.requests.Session.get')
    @patch('cafop_services.scraper.requests.Session.post')
    def test_get_cafop_affectation_not_found(self, mock_post, mock_get):
        mock_get.return_value.status_code = 200
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Introuvable dans la base"
        mock_post.return_value = mock_response

        result = get_cafop_affectation("123456")
        self.assertEqual(result["status"], "error")
        self.assertTrue("non trouvé" in result["message"])

    @patch('cafop_services.scraper.requests.get')
    def test_get_cafop_directors_directory(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'''
        <html>
            <table>
                <tr><th>CAFOP</th><th>Directeur</th></tr>
                <tr><td>CAFOP Abidjan</td><td>Monsieur X</td></tr>
            </table>
        </html>
        '''
        mock_get.return_value = mock_response

        result = get_cafop_directors_directory()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["data"][0]["CAFOP"], "CAFOP Abidjan")

if __name__ == '__main__':
    unittest.main()
