import difflib
import sys
import glob
import lichen
import re

import logging


logging.basicConfig()

class LichenTester:
    
    def __init__(self,paths:list[str]):
        self.lcpaths:list[str] = paths
    
    def test_all(self):
        """

        """
        for lcpath in self.lcpaths:
            with open(lcpath,mode="r",encoding="utf-8") as f:
                test_case = f.read()
                print(" input :{}".format(lcpath).center(100,"-"))
                print(test_case)
                sparser = lichen.State_parser(test_case)
                print(" output ".center(100,'-'))
                
                print(sparser.toplevel_resolve())

def test00():
    paths = glob.glob("./test_set/*test.lc")
    tester = LichenTester(paths)
    print("test start".center(100,"="))
    tester.test_all()


if __name__=="__main__":
    args = sys.argv
    if args[1] == "0":
        test00()
    else:
        print("else")

