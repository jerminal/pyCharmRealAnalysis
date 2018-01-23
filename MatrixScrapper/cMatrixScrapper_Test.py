import unittest
from  MatrixScrapper import cMatrixScrapper

class MSTest(unittest.TestCase):
    def testSFH_Result_Details_Page(self):
        file = '..\\testData\\sfh.html'
        with open(file, 'r') as s:
            sHtml = s.read()
        oMS = cMatrixScrapper('RealAnalysisConfig.xml', 'DEV')


        return


if __name__ == "__main__":
    unittest.main()