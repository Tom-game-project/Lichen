import lichen

import difflib
from pprint import pprint

class Tester:
    """
    # tester
    テストクラス
    期待するコードと実際に出力されるコードの差分を表示する
    """
    def __init__(
            self,
            question:list[str],
            answer:list[str]
        ) -> None:
        self.question = question
        self.answer = answer
    
    def test(self):
        """
# test
## 期待するコードと実際に出力されるコードの差分を表示する
        """
        for i,(q,a) in enumerate(zip(self.question,self.answer)):
            print("test{:d}".format(i).center(80,"="))
            res = difflib.unified_diff(q.split(), a.split())
            res = "\n".join(res)
            if len(res) == 0:
                print("ok")
            else:
                print("error!")
                print(res)
     

def __test_00():
    print("""
# __test_00
""")
    pass

def __test_01():
    print("""

""")
    a = lichen.Parser("")
    # expr test cases
    test_cases:list = list()
    with open("../examples/ex03.lc") as f :test_cases = [i for i in f]
    # print(test_cases)
    for testcase in test_cases:
        codelist = a.code2vec(testcase)
        pprint(codelist)
        print()

def __test_02():
    print(
"""
# __test_02
""")
    a = lichen.Parser("")
    # expr test cases
    statement_test_cases = [
"""
pub fn add(a:i32,b:i32):i32
{
    return a + b;
}
const a = for (i <- list){
    const flag = string==i;
    if (if (flag){1} else {0}){
        const a = "hello" + "world";
        print("hello" + "world");
    };
}
""",
"""
loop {
    print("hello");
};
""",
    ]
    for testcase in statement_test_cases:
        codelist = a.code2vec(testcase)
        print(testcase)
        pprint(codelist)
        print()

def __test_03():
    print("""
    # __test_03
    ## 文パーサの動作テスト
    """)
    expr_test_cases=[
"""
fn add(a:i32,b:i32):i32{
    return a + b;
}

pub fn sub(a:i32,b:i32):i32{
    let c = a - b;
    return c;
}
fn main (a:i32,b:i32):void{
    let c = add(1,2);
    let d:i32 = a / (b*(c+d));
    c += 1;
    d = d + 42;
    return d;
}
""",
"""
let a = if (expr){return 0;}else{return 1} + a;
""",
"""
pub fn gcd(a:i32,b:i32):i32{
    if b == 0{
        return a;
    }else{
        return gcd(b,a%b);
    };
}
""",
"""
if (num % 15 == 0)
{
	print("fizzbazz");
}
elif (num % 3 == 0)
{
	print("fizz");
}
elif (num % 5 == 0)
{
	print("bazz");
}
else
{
	print(num);
}
""",
"let a:i32;",
"""
fn func00(a : bool) : bool{
    if (0 < a){
        let r = True;
        return r;
    }else{
        let r = False;
        return r
    };
}
""",
"""
fn func00(a : bool) : bool{
    let r = True;
    return r;
}
""",
"""
fn func00(a :i32) : i32{
    let r:i32 = if (a){
        let val0:i32 = 10;
        b
    } else {
        let val1:i32 = 10;
        c
    };
    return r;
}
""",
"""
fn aa():i32{
    print();
}
"""
    ]

    for i,testcase in enumerate(expr_test_cases):
        a = lichen.State_parser(testcase) #constract expr parser
        codelist = a.resolve()
        print(f"test{str(i).rjust(2,'0')}".center(40,'='))
        print("sample state: ",testcase)
        print("result: ",codelist)
        for elem in codelist:
            # print(elem)
            if type(elem) is lichen.DecFunc:
                # print(elem)
                print(elem.wat_format_gen())
            else:
                #print(repr(elem) + "is not dec")
                pass
        print()

def __test_04():
    print("""
# __test_04
## 式パーサの動作テスト
""")
    expr_test_cases = [
        "a[0]",
        "func()[0][1+a]",
        "print(hello[0],\"world\"+\"!\")",
        "a / (b*(c+d))",
        "2*cube(x)+3*squared(x)+3",
        "a*b*c",
        "a + b * c",
        "-a + -c",
        "a**b**c",
        "a[0]**b[0][1]**c[0][1][2]",
        "!f(a,b)",
        "2** -1",
        "2**-1**-1 - 1 - 1", # (2**(-(1**(-1)))) -1-1
        "if (expr){return 1;}elif (expr2){pass;}else{return 0;} + loop {break 4;}"
    ]
    
    a = lichen.Expr_parser("")
    for i,testcase in enumerate(expr_test_cases):
        codelist = a.code2vec(testcase)
        print(i)
        print("sample expr:",testcase)
        pprint(codelist)
        # print("minimun priority index:",a.find_min_priority_index(codelist))
        print()

def __test_05():
    print("""
# __test_05
## コンマ区切り
""")
    expr_test_cases = [
        "\"hello\",\"world\",\"Tom!\"",
        "0,1,2 ,3,4, 5 ,6,7  ,8,9,10",
        "func00(),func01(1),func02(1,2)",
        "0,1,2 ,3.14,4, 5 ,6,7  ,8,9,10,",
        "mut a:i32,mut b:i32"
    ]
    
    for testcase in expr_test_cases:
        a = lichen.Parser(testcase)
        codelist = a.resolve()
        print("sample expr:",testcase)
        pprint(codelist)
        # print("minimun priority index:",a.find_min_priority_index(codelist))
        print()

def __test_06():
    print("""
# __test_06
## 式パーサの動作テスト
""")
    expr_test_cases = [
        "func()[0][1+a]",
        "print(hello[0],\"world\"+\"!\")",
        "a / (b*(c+d))",
        "2*cube(x)+3*squared(x)+3",
        "a*b*c",
        "a + b * c",
        "-a + -c",
        "a**b**c",
        "a[0]**b[0][1]**c[0][1][2]",
        "!f(a,b)",
        "2** -1",
        "2**-1**-1 - 1 - 1", # (2**(-(1**(-1)))) -1-1
        "if (expr){return 1;}elif (expr2){pass;}else{return 0;} + loop {break 4;}",
        """
        0 <= if (i % 2 == 0)
        {
            return i/2;
        }
        else
        {
            i*3 + 1
        } + add(1,2,3)
        """,
        """
        for (i <- range(10))
        {
            print("hello world");
            print("hello world");
            j += i
        }
        else
        {
            return j;
        } + add(1 , 1)
        """,
        " 10 + ( x + log10(2) * sin(x) ) * log10(x)",
        "(-sin(x)*3)+(-2*cos(x))",
        "pi",
        "gcd(a,b)",
        "sin(x)",
        "(1)+2",
        "3.14",
        "-812+42",
        "a / b*(c+d)",
        "a / (b*(c+d))",
        "a*a*a",
        "x^3+x^2+3",
        "2*cube(x)+3*squared(x)+3",
        "10<=d<100",
        "[a+b,0,0]",
        "a[0][0]+a[0][1] * arr(a)[0][2] * if (expr) { [0,1] } else{ [1,0] } [0]",
        "a = a + 1",
        "a += 1",
        """
a = if (a % 2 == 0){
    logger(a);
    return a / 2;
}else{
    logger(a);
    return 3*a + 1;
}
"""
    ]
    
    for i,testcase in enumerate(expr_test_cases):
        a = lichen.Expr_parser(testcase)
        codelist = a.resolve()
        print(f"test{str(i).rjust(2,'0')}".center(40,'='))
        print("sample expr:",testcase)
        print("result:",codelist)
        # print("minimun priority index:",a.find_min_priority_index(codelist))
        print()


def __diff_test_00():
    print(
"""
# __diff_test_00
""")
    test_list:list = [
        "a / b*(c+d)",
        "a / (b*(c+d))",
        "3+2*5",
        "gcd(b,a%b)",
        "b = 97 <= a && a<= 122",
    ]
    output_list:list = [
"""
local.get $a
local.get $b
i32.div_u
local.get $c
local.get $d
i32.add
i32.mul
""",
"""
local.get $a
local.get $b
local.get $c
local.get $d
i32.add
i32.mul
i32.div_u
""",
"""
i32.const 3
i32.const 2
i32.const 5
i32.mul
i32.add
""",
"""
local.get $b
local.get $a
local.get $b
i32.rem_u
call $gcd
""",
"""

""",
"""
""",

    ]
    input_list = []
    for i in test_list:
        print("sample:",i)
        expr_parser = lichen.Expr_parser(i)
        codelist = expr_parser.resolve()
        wasm = codelist[0].wat_format_gen()
        print(wasm)
        input_list.append(wasm)
    # (a (b (c d i32.add) i32.mul) i32.div_u)
    tester = Tester(input_list,output_list)
    tester.test()
    


def __diff_test_01():
    print(
"""
# __diff_test_01
""")
    test_list:list = [
"""
pub fn f(a:i32,b:i32):i32{
    print_i32(1);
    return 1+1;
}
"""
    ]
    output_list:list = [
""""""
    ]
    input_list = []
    for i in test_list:
        print("sample:",i)
        expr_parser = lichen.State_parser(i)
        codelist = expr_parser.resolve()
        print(codelist)
        print()
        wasm = codelist[0].wat_format_gen()
        print(wasm)
        input_list.append(wasm)
    # (a (b (c d i32.add) i32.mul) i32.div_u)
    tester = Tester(input_list,output_list)
    tester.test()
    

if __name__=="__main__":
    # __test_02()
    __test_03()
    #__test_06()
    #__diff_test_00()
    #__diff_test_01()

