# -*- coding: utf-8 -*-
"""
Created on Fri May 24 15:41:00 2013

@author: proto
"""

import unittest
import libsbml2bngl
from evaluate import evaluate
from os import listdir
from os.path import isfile, join
import copasi

##Taken from: http://eli.thegreenplace.net/2011/08/02/python-unit-testing-parametrized-test-cases/

class ParametrizedTestCase(unittest.TestCase):
    """ TestCase classes that want to be parametrized should
        inherit from this class.
    """
    def __init__(self, methodName='runTest', param=None):
        super(ParametrizedTestCase, self).__init__(methodName)
        self.param = param

    @staticmethod
    def parametrize(testcase_klass, param=None):
        """ Create a suite containing all tests taken from the given
            subclass, passing them the parameter 'param'.
        """
        testloader = unittest.TestLoader()
        testnames = testloader.getTestCaseNames(testcase_klass)
        suite = unittest.TestSuite()
        for name in testnames:
            suite.addTest(testcase_klass(name, param=param))
        return suite
        
class TestOne(ParametrizedTestCase):
    '''
    Test for ability to ruleify
    '''
    def test_parsing(self):
        #reactionDefinitions, useID = libsbml2bngl.selectReactionDefinitions('BIOMD%010i.xml' % self.param)
        #spEquivalence = detectCustomDefinitions(bioNumber)
        print self.param
        libsbml2bngl.analyzeFile('XMLExamples/curated/BIOMD%010i.xml' % self.param, 'reactionDefinitions/reactionDefinition7.json',
                    False, 'config/namingConventions.json',
                    'raw/output' + str(self.param) + '.bngl', speciesEquivalence=None,atomize=False,bioGrid=False)


class TestEval(ParametrizedTestCase):
    """
    Test for whether a file is able to be simulated by bionetgen
    """
    def test_eval(self):
        fileName = self.param
        print fileName
        self.assertEqual(evaluate(fileName),0)

class TestCopasi(ParametrizedTestCase):
    """
    Test for whether the time series generated by a translated version matches that of
    the original one
    """
    def test_copasi(self):
        fileNumber = self.param
        score = copasi.evaluate(fileNumber)
        self.assertAlmostEqual(score, 0, delta=1e-2)
    
def getValidBNGLFiles(directory):
    """
    Gets a list of bngl files that could be correctly translated in a given 'directory'
    """
    onlyfiles = [ f for f in listdir('./' + directory) if isfile(join('./' + directory, f)) ]
    
    logFiles = [x[0:-4] for x in onlyfiles if 'log' in x]
    errorFiles = []
    #dont skip the files that only have warnings    
    for log in logFiles:    
        with open('./' + directory + '/' + log +'.log','r') as f:
            k = f.readlines()
            if 'ERROR' in ','.join(k):
                errorFiles.append(log)
    bnglFiles = [x for x in onlyfiles if 'bngl' in x and 'log' not in x and 'dict' not in x]
    validFiles = [x for x in bnglFiles if x not in errorFiles]
    import re
    validNumbers = []
    for x in validFiles:
        number = re.search('output([0-9]+)',x)    
        if number != None:
            validNumbers.append(number.group(1))
        
    return validNumbers

def getValidGDats(directory):
    onlyfiles = [ f for f in listdir('./' + directory) if isfile(join('./' + directory, f)) ]
    gdatFiles = [x for x in onlyfiles if 'gdat' in x]
    validNumbers = []
    import re
    for x in gdatFiles:
        number = re.search('output([0-9]+)',x)    
        if number != None:
            validNumbers.append(number.group(1))
        
    return validNumbers

    
if __name__ == "__main__":      
    suite = unittest.TestSuite()
    ran = range(1,464)
    #ran.remove(52)
    #ran.remove(205)
    #ran.remove(235)
    #ran = [229]
    '''
    ran = [244, 19, 183, 144, 268, 450, 152, 406, 446, 265, 235, 88, 175, 412,
           147, 338, 297, 293, 49, 344, 83, 230, 453, 223, 109, 56, 256, 410, 
           340, 452, 286, 399, 445, 285, 457, 74, 250, 334, 227, 205, 339, 151, 
           424, 14, 153, 105, 407, 451, 332, 326, 255, 356]
    ''' 
    #ran = [229]
    #ran  = [5,6,7,36,56,107,111,144,195,265,297,306,307,308,309,310,311,312]       
    #ran  = [120]    
    for index in ran:
         suite.addTest(ParametrizedTestCase.parametrize(TestOne, param=index))
    #for fileName in validFiles:
        
    validFiles = getValidBNGLFiles('raw') 
    validFiles = sorted(validFiles)
    #validFiles.remove('54')
    for fileNumber in validFiles:
        fileName = 'output{0}.bngl'.format(fileNumber)
        suite.addTest(ParametrizedTestCase.parametrize(TestEval,param='./raw/' + fileName))
    validGdats = getValidGDats('.')
    
    validFiles = getValidBNGLFiles('raw')
    #for fileNumber in validFiles:
    #    fileName = 'output{0}.bngl'.format(fileNumber)
    #    suite.addTest(ParametrizedTestCase.parametrize(TestEval,param='./raw/' + fileName))
    for index in validGdats:
        suite.addTest(ParametrizedTestCase.parametrize(TestCopasi, param=index))
       
    unittest.TextTestRunner(verbosity=2).run(suite)

