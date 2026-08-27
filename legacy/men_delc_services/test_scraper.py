import unittest
from unittest.mock import patch, MagicMock
from men_delc_services.scraper import get_textes_officiels, get_drena_directory, get_primaire_nominations

class TestMenDelcScraper(unittest.TestCase):
    
    @patch('men_delc_services.scraper.requests.get')
    def test_get_textes_officiels_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'<html><a href="/static/docs/test.pdf">Decret Test</a></html>'
        mock_get.return_value = mock_response

        result = get_textes_officiels()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["textes"][0]["titre"], "Decret Test")

    @patch('men_delc_services.scraper.requests.get')
    def test_get_drena_directory_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'''
        <html>
            <table>
                <tr><th>DRENA</th><th>Contact</th></tr>
                <tr><td>Abidjan 1</td><td>01020304</td></tr>
            </table>
        </html>
        '''
        mock_get.return_value = mock_response

        result = get_drena_directory()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["data"][0]["DRENA"], "Abidjan 1")

if __name__ == '__main__':
    unittest.main()
