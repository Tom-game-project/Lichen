"""
# test2
Lichen のテスト用ファイル

"""
import difflib
import sys
import glob
import lichen
import re

import logging


logging.basicConfig()

class LichenTester:
    """
    # LichenTester
    テスト用のクラス
    """
    def __init__(self,paths:list[str]):
        self.lcpaths:list[str] = paths
    
    def test_all(self):
        """

        """
        for lcpath in self.lcpaths:
            out_wat_text:str = ""
            with open(lcpath,mode="r",encoding="utf-8") as f:
                test_case = f.read()
                print(" input :{}".format(lcpath).center(100,"-"))
                print(test_case)
                sparser = lichen.State_parser(test_case)
                print(" output ".center(100,'-'))
                print(sparser.resolve())
                print(sparser.toplevel_resolve())
                out_wat_text = sparser.toplevel_resolve()
            regex = re.compile(r"(ex\d\d)\.test\.lc")
            mo = regex.search(lcpath)
            print(mo.group(0),mo.group(1))
            with open("./dist/{}.wat".format(mo.group(1)),mode="w",encoding="utf-8") as f:
                f.write(out_wat_text)

def test00():
    # paths = glob.glob("./test_set/*test.lc")
    paths = [
        "test_set/ex00.test.lc",
        "test_set/ex01.test.lc",
        "test_set/ex02.test.lc",
    ]
    tester = LichenTester(paths)
    print("test start".center(100,"="))
    tester.test_all()

def test01():
    # paths = glob.glob("./test_set/*test.lc")
    paths = [
        "test_set/ex05.test.lc",
    ]
    # tester = LichenTester(paths)
    # print("test start".center(100,"="))
    # tester.test_all()
    with open("test_set/ex05.test.lc",mode="r",encoding="utf-8") as f:
        p = lichen.State_parser(f.read())
        codelist = p.resolve()
        for i in codelist:
            print()
            print(i)




if __name__=="__main__":
    args = sys.argv
    if args[1] == "0":
        test00()
    elif args[1] == "1":
        test01()
    else:
        print("else")

