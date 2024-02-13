from enum import Enum,auto

# debug tools
from pprint import pprint
import logging


logging.basicConfig(level=logging.DEBUG)


class Control(Enum):
    IF   = auto()
    ELIF = auto()
    ELSE = auto()
    THEN = auto()
    WHILE = auto()
    LOOP = auto()
    FOR = auto()


class Control_parser:
    def __init__(self, code:str) -> None:
        self.code = code
        
        # const
        self.OPENBRACE = '{'
        self.CLOSEBRACE = '}'

        self.OPENSQUAREBRACKET = '['
        self.CLOSESQUAREBRACKET = ']'

        self.DOUBLEQUOTATION = '"'
        self.SINGLEQUOTATION = '\''
        self.ESCAPESTRING = "\\"

    def resolve(self):
        pass

    # クォーテーションをまとめる
    def resolve_quatation(self,strlist:list[str],quo_char) -> list[str]:
        open_flag:bool = False
        escape_flag:bool = False
        rlist:list = list()
        group:list = list()
        for i in strlist:
            if escape_flag:
                group.append(i)
                escape_flag = False
            else:
                if i == quo_char:
                    if open_flag:
                        group.append(i)
                        rlist.append("".join(group))
                        group.clear()
                        open_flag = False
                    else:
                        group.append(i)
                        open_flag = True
                else:
                    if open_flag:
                        if i == self.ESCAPESTRING:
                            escape_flag = True
                        else:
                            escape_flag = False
                        group.append(i)
                    else:
                        rlist.append(i)
        return rlist

    # ブロックごとにまとめる
    def resolve_block(self,strlist:list[str]) -> list[str]:
        depth:int = 0
        rlist:list = list()
        group:list = list()
        for i in strlist:
            if i == self.OPENBRACE:
                if depth>0:
                    group.append(i)
                elif depth == 0:
                    group.append(i)
                else:
                    print("Error!")
                    return
                depth += 1
            elif i== self.CLOSEBRACE:
                depth -= 1
                if depth > 0:
                    group.append(i)
                elif depth == 0:
                    group.append(i)
                    rlist.append("".join(group))
                    group.clear()
                else:
                    print("Error!")
                    return
            else:
                if depth > 0:
                    group.append(i)
                elif depth == 0:
                    rlist.append(i)
                else:
                    print("Error!")
                    return 
        return rlist

    # ブロック
    def resolve_sq_bracket():
        pass


class parser:
    def __init__(self,code):
        self.code:str = code


#test

def __test_00():

    code_sample_00:str = """
    fn fizzbazz(a:i32):void{
        if a % 15 == 0{
            print("fizzbazz");
        }elif a % == 3{
            print("fizz");
        }elif a % == 5{
            print("bazz");
        }else{
            print(a);
        }
    }
    fn main(){
        // コメント、コメント
        for i in 0..100 {
            fizzbazz(i);
        }
    }
    """
    code_sample_01 = """
    fn gcd(a:i32,b:i32):i32{
        if b == 0{
            return a;
        }else{
            return gcd(b,a%b);//コメント
        }
    }
    fn main(){
        let a = 123456789;
        let b = 987654321;
        debug("gcd(%d, %d) -> %d", a, b, gcd(a, b));
    }
    s"""

def __test_01():
    """
    # single or double quotation test
    """
    a = Control_parser("hello")
    code = """
let code : String = "\\"hello\\"";
let code : String = "hello 

world";
"""
    print (
        a.resolve_quatation(code,a.DOUBLEQUOTATION)
    )

def __test_02():
    """
    # brace test
    """
    a = Control_parser("")
    code = """
fn main (void)
{
if (){
    print("hello world")
}
}
"""
    codelist = a.resolve_quatation(code,a.DOUBLEQUOTATION)
    codelist = a.resolve_block(codelist)
    for i,j in enumerate(codelist):
        print(i,j)


if __name__=="__main__":
    __test_02()
