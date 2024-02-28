import parser
from pprint import pprint


def __test_00():
    pass

def __test_01():
    a = parser.parser("")
    # expr test cases
    test_cases:list = list()
    with open("../examples/ex03.lc") as f :test_cases = [i for i in f]
    # print(test_cases)
    for testcase in test_cases:
        codelist = a.code2vec(testcase)
        pprint(codelist)
        print()

def __test_02():
    """
    # __test_04
    ## expr test

    
    """
    a = parser.parser("")
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
    """
    # __test_03
    ## expr test

    """
    expr_test_cases=[
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
        "a[0][0]+a[0][1] * arr(a)[0][2] * if (expr) { [0,1] } else{ [1,0] } [0]",
    ]

    a = parser.Expr_parser("") #constract expr parser
    for testcase in expr_test_cases:
        codelist = a.code2vec(testcase)
        print(testcase)
        pprint(codelist)
        print()

def __test_04():
    expr_test_cases = [
        "a / (b*(c+d))",
        "2*cube(x)+3*squared(x)+3",
        "a*b*c",
        "!f(a,b)",
        "2** -1"
    ]
    
    a = parser.Expr_parser("")
    for testcase in expr_test_cases:
        codelist = a.code2vec(testcase)
        print("sample expr:",testcase)
        pprint(codelist)
        print()

if __name__=="__main__":
    # __test_02()
    __test_04()
