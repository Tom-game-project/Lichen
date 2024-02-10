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
    def __init__(self) -> None:
        pass

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

    def resolve(self):
        pass

    def resolve_if(self,code:str):
        pass

    def resolve_block():
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


if __name__=="__main__":
    __test_00()
