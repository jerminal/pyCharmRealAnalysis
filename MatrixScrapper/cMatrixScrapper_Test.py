import unittest
from MatrixScrapper import cMatrixScrapper as MS

class MSTest(unittest.TestCase):
    def setUp(self):
        try:
            self._oMS = MS('AllPropScrapper', 'DEV')
        except:
            print(MS.__file__)
            raise

    def testSFH_Result_Details_Page(self):
        file = '..\\testData\\sfh.html'
        with open(file, 'r') as s:
            sHtml = s.read()
        self._oMS.ScrapSearchResultPropertyDetail(sHtml)

        return


if __name__ == "__main__":
    unittest.main()