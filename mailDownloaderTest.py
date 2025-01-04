import unittest
import argparse
from email_reader import find_urls_in_email
from mail_downloader import download, download_all_uris
import logging as log

def configure_log():
    log.basicConfig(
    level=log.INFO,
    format='%(asctime)s,%(funcName)s,%(levelname)s,%(thread)d,%(message)s',
    handlers=[
        log.StreamHandler()
        ]
    )
    
class TestMailParser(unittest.TestCase):
        def test_url_detection(self):
            email_content = [
            "Chopin - 7 Polonaises Op. 26, 40, 44, 53, 61 - Vladimir Ashkenazy",
            "https://www.youtube.com/watch?v=Pp4v42suFQg from 5.00 till 6.00 and from 37.03 till 43.17",
            "Tchaikovsky - Eugene Onegin, Polonaise - Temirkanov",
            "https://www.youtube.com/watch?v=k0diQumrDmg 4.23",
            "Aida Garifullina, Giacomo Puccini: Quando m'en vo (La Bohème, Musetta's Waltz)",
            "https://www.youtube.com/watch?v=NJaKA7d8jV8 2.53",
            "Pavarotti- Rossini- La Danza",
            "https://www.youtube.com/watch?v=2DbwrU3QZsA 3.18",
            "Alfredo Kraus - Siciliana (Mascagni - Cavalleria rusticana)",
            "https://www.youtube.com/watch?v=BX9lY8A3f8w 2.23"
            ]
            urls = find_urls_in_email(email_content, log)
            print(urls)
            self.assertEqual(len(urls), 5)
        
        # def test_download_file(self):
        #     configure_log()
        #     link = "https://www.youtube.com/watch?v=BX9lY8A3f8w"
        #     download(link, log)
            
        # def test_download_multiple(self):
        #     configure_log()
        #     email_content = [
        #     "K Vilensky Variations On The Themes By Bac",
        #     "https://www.youtube.com/watch?v=z3nY7lJztcM till 2.23                                National Philharmonic Society of Ukraine, Kiev, 12.01.14",
        #     "Mischa Maisky plays Bach Cello Suite No.1 in G (full)",
        #     "https://www.youtube.com/watch?v=mGQLXRTl3Z0 till 2.44",
        #     "Kerson Leong and Ryan Roberts play Bach: Concerto for Oboe and Violin - 3rd movement",
        #     "https://www.youtube.com/watch?v=NJaKA7d8jV8 2.53",
        #     "Pavarotti- Rossini- La Danza",
        #     "https://www.youtube.com/watch?v=eRwikZiIYdM 3.51"
        #     ]
        #     urls = find_urls_in_email(email_content, log)
        #     file_infos = download_all_uris(urls, log)

            
            
            
            
if __name__ == '__main__':
    unittest.main()
