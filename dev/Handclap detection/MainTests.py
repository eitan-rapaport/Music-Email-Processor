# pylint: disable=missing-function-docstring,missing-module-docstring

import unittest
import argparse
from classification_results import ClassificationResults
from DownloadMomsEmails import remove_leading_handclaps

class TestStringMethods(unittest.TestCase):
    
    def parse_args(self):
        parser = argparse.ArgumentParser(
        description='Download Youtube videos as wav and mp4 and normalize them',
        prog='Download Youtube MP3')
        parser.add_argument('--debug', action='store_false', default=True,
                            help='Debug configuration')
        return parser.parse_args()

    def test_leading_handclaps_detection(self):
        args = self.parse_args()
        print(args)
        cr = ClassificationResults(name="Luciano Pavarotti Una furtiva lacrima 2J7JM0tGgRY.wav",
                                silence=[263],
                                applause=[1, 2, 3, 296, 297, 298, 299, 300, 301, 302, 304,
                                          305, 306, 307, 308, 310, 311, 312, 313, 314, 315,
                                          316, 317, 318, 319, 320, 321, 322, 323, 324, 325,
                                          326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336,
                                          337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347,
                                          348, 349, 350, 351, 352, 353, 354, 356, 357,
                                          358, 359, 360, 361, 362, 363, 364, 365, 366, 367,
                                          368, 369, 370, 371, 372, 373, 374, 375, 376, 377,
                                          378, 379, 380, 381],
                                speech=[4, 5, 153, 242, 243, 244, 254, 255, 256, 264, 272, 273],
                                length=382
                                )
        list_of_cr = []
        list_of_cr.append(cr)
        self.assertTrue(remove_leading_handclaps(list_of_cr, arguments=args))

if __name__ == '__main__':
    unittest.main()
