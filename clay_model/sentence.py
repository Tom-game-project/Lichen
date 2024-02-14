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


class Object_tag(Enum):
    """
    # Object tag
    """
    # 未定義
    UNDEF = auto()
    # 文字列
    STRING = auto()

    # block
    SQBLOCK = auto()
    BLOCK = auto()

    # 式
    EXPR = auto()



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

        # if, elif, else
        self.if_string = "if"
        self.elif_string = "elif"
        self.else_string = "else"

        # loop,while,for
        self.loop_string = "loop"
        self.while_string = "while"
        self.for_string = "for"

    def resolve(self):
        pass

    # クォーテーションをまとめる
    def resolve_quatation(self,strlist:list[str], quo_char:str) -> list[(Object_tag,str)]:
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
                        #group.append(i)
                        rlist.append((Object_tag.STRING,"".join(group)))
                        group.clear()
                        open_flag = False
                    else:
                        #group.append(i)
                        open_flag = True
                else:
                    if open_flag:
                        if i == self.ESCAPESTRING:
                            escape_flag = True
                        else:
                            escape_flag = False
                        group.append(i)
                    else:
                        rlist.append((Object_tag.UNDEF,i))
        return rlist

    # ブロックごとにまとめる
    def resolve_block(self,strlist:list[(Object_tag,str)],open_block_char:str,close_block_char:str,object_tag:Object_tag) -> list[str]:
        depth:int = 0
        rlist:list = list()
        group:list = list()
        for elem_type_tag,i in strlist:
            if i == open_block_char and elem_type_tag is Object_tag.UNDEF:
                if depth>0:
                    group.append(i)
                elif depth == 0:
                    #group.append(i)
                    pass
                else:
                    print("Error!")
                    return
                depth += 1
            elif i == close_block_char and elem_type_tag is Object_tag.UNDEF:
                depth -= 1
                if depth > 0:
                    group.append(i)
                elif depth == 0:
                    #group.append(i)
                    rlist.append((object_tag,"".join(group)))
                    group.clear()
                else:
                    print("Error!")
                    return
            else:
                if depth > 0:
                    group.append(i)
                elif depth == 0:
                    rlist.append((elem_type_tag,i))
                else:
                    print("Error!")
                    return 
        return rlist
    
    def resolve_modifier(self,strlist:list[(Object_tag, str)]) -> list[str]:
        # ここは文法に直結する、やや面倒な処理になる
        # exprがどこまでなのかを判別する方法をしっかりさせないといけない
        pass #todo

    def resolve_iewf(self,strlist:list[(Object_tag, str)],syntax_string:str) -> list[(Object_tag, str)]:
        """
        if , elif , for , while の四つの文法のうちいずれかに関して解決する
        ここでは、上の4つの文法のうちいずれかを発見する、そして、文法文字列と、ブロック間に存在する式をまとめる
        """
        size = len(strlist)
        group:list = list()
        rlist:list = list()

        for index,(elem_type_tag,i) in enumerate(strlist[:size - len(syntax_string)]):
            pass
        return rlist


class Control_parse_tree:
    def __init__(self,type_,expr,proc:"Control_parse_tree") -> None:
        self.expr = expr

class parse_element:
    # tree状になったparseオブジェクト
    def __init__(self,type_:str,contents:str):
        self.type_ = type_
        self.contents = contents

    def get_type(self):
        return self.type_
    

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
    """

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
a[0:5]
{hello world}
if a == "{"{
    print("hello world")
}

fn main (void){
    if (){
        print("hello world"[0:5])
    }
}

"""
    codelist = a.resolve_quatation(code,a.DOUBLEQUOTATION)
    codelist = a.resolve_block(codelist,a.OPENSQUAREBRACKET,a.CLOSESQUAREBRACKET,Object_tag.SQBLOCK)
    codelist = a.resolve_block(codelist,a.OPENBRACE,a.CLOSEBRACE,Object_tag.BLOCK)
    for i,j in enumerate(codelist):
        print(str(i).rjust(2),j)

def __test_03():
    code = """
if string == "{"{
    print("hello world")
}
"""


if __name__=="__main__":
    __test_02()
