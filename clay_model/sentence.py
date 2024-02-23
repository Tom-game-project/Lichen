from enum import Enum,auto

# debug tools
from pprint import pprint
import logging


logging.basicConfig(level=logging.DEBUG)


class Object_tag(Enum):
    """
    # Object tag
    """
    # 未定義
    UNDEF = auto()

    # 文字列
    STRING = auto()    # a-zA-Z

    # block
    SQBLOCK = auto()   # []
    PARENBLOCK = auto()# ()
    BLOCK = auto()     # {}

    # 式
    EXPR = auto()

    # 制御文法
    CONTROL = auto()

    # 単語
    WORD = auto()


class Control_parser:
    def __init__(self, code:str) -> None:
        self.code = code
        
        # const
        self.OPENBRACE = '{'
        self.CLOSEBRACE = '}'

        self.OPENSQUAREBRACKET = '['
        self.CLOSESQUAREBRACKET = ']'

        self.OPENPAREN = '('
        self.CLOSEPAREN = ')'

        self.DOUBLEQUOTATION = '"'
        self.SINGLEQUOTATION = '\''
        self.ESCAPESTRING = "\\"

        # # if, elif, else
        # self.if_string = "if"
        # self.elif_string = "elif"
        # self.else_string = "else"

        # # loop,while,for
        # self.loop_string = "loop"
        # self.while_string = "while"
        # self.for_string = "for"

    def resolve0(self,code:str) -> list["parse_element"]:
        codelist = self.resolve_quatation(code,self.DOUBLEQUOTATION)
        return codelist

    def resolve1(self,codelist:list["parse_element"]):
        codelist = self.resolve_block(codelist,self.OPENSQUAREBRACKET,self.CLOSESQUAREBRACKET,     Object_tag.SQBLOCK) # []
        codelist = self.resolve_block(codelist,        self.OPENPAREN,        self.CLOSEPAREN,  Object_tag.PARENBLOCK) # ()
        codelist = self.resolve_block(codelist,        self.OPENBRACE,        self.CLOSEBRACE,       Object_tag.BLOCK) # {}
        print(codelist)
        print("="*40)
        codelist = self.grouping_word(codelist,["\t","\n"," "],["if","elif","else","white","loop"])
        #codelist = self.grouping_control_syntax0(codelist,["if","elif","else","white","loop"])
        return codelist

    def resolve2(self,codelist:list["parse_element"]):
        return codelist

    # クォーテーションをまとめる
    def resolve_quatation(self,strlist:list[str], quo_char:str) -> list["parse_element"]:
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
                        rlist.append(parse_element.new(Object_tag.STRING,None,None,"".join(group)))
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
                        rlist.append(parse_element.new(Object_tag.UNDEF,None,None,i)) # undefのときはそのまま
        return rlist

    # ブロックごとにまとめる
    def resolve_block(self,strlist:list["parse_element"],open_block_char:str,close_block_char:str,object_tag:Object_tag) -> list["parse_element"]:
        depth:int = 0
        rlist:list = list()
        group:list = list()
        for par_elem in strlist:
            i = par_elem.contents
            elem_type_tag = par_elem.get_type
            if elem_type_tag is Object_tag.UNDEF and i == open_block_char:
                if depth>0:
                    group.append(par_elem)
                elif depth == 0:
                    #group.append(i)
                    pass
                else:
                    print("Error!")
                    return
                depth += 1
            elif elem_type_tag is Object_tag.UNDEF and i == close_block_char:
                depth -= 1
                if depth > 0:
                    group.append(par_elem)
                elif depth == 0:
                    #group.append(i)
                    if object_tag is Object_tag.SQBLOCK:
                        rlist.append(parse_element.new(object_tag, None, list(group), None)) # 不明な挙動
                    elif object_tag is Object_tag.PARENBLOCK:
                        rlist.append(parse_element.new(object_tag, None, list(group), None)) # 不明な挙動
                    elif object_tag is Object_tag.BLOCK:                                     # Object_tag.
                        rlist.append(parse_element.new(object_tag, None, None, self.resolve1(group)))
                    else:
                        print("Error!")
                        return 
                    group.clear()
                else:
                    print("Error!")
                    return
            else:
                if depth > 0:
                    group.append(par_elem)
                elif depth == 0:
                    rlist.append(par_elem)
                else:
                    print("Error!")
                    return 
        
        return rlist

    def grouping_word(self,strlist:list["parse_element"], split_str:str, control_str:str) -> list["parse_element"]:
        """
        文法規則に基づいて、単語をまとめる
        split_str = ["\t","\n"," "]
        ```python
        grouping_word(strlist:list["parse_element"], split_str = ["\t","\n"," "], control_str = ["if","elif","else","while","loop"]) -> list["parse_element"]:
        ```
        """
        rlist:list = list()
        group:list = list()
        expr_flag:bool = False
        pre_word_is_not_contlol:bool = True

        for par_elem in strlist:

            # strlistはすでに、文字列ブロックへとグループされている
            if par_elem.get_type is Object_tag.UNDEF: # タイプが未定義であった場合
                if par_elem.contents in split_str: # 区切り文字であった場合
                    if group:                     # もし単語グループがあれば
                        word = "".join(group)
                        pre_word_is_not_contlol = word not in control_str
                        rlist.append(parse_element.new(Object_tag.WORD,word, None, None))
                        group.clear()
                    else:                         # なければ
                        rlist.append(par_elem)
                # elif par_elem.contents == "=" and not expr_flag:    # "="を見つけたとき、直後に見つけた単語が制御文字でなければ("=="をカウントしてしまう可能性をなくす)
                #     if group:                     # 単語グループがあれば
                #         word = "".join(group)
                #         pre_word_is_not_contlol = word not in control_str
                #         print(word)
                #         rlist.append(parse_element.new( Object_tag.WORD, word, None, None))
                #         group.clear()
                #     else:                         # なければ
                #         rlist.append(par_elem)
                #     expr_flag = True
                elif par_elem.contents == ";": # ";"を見つけたとき、そして、式フラグが立っているとき
                    if group:                                # 式グループがあれば
                        rlist.append(parse_element.new( Object_tag.WORD, None, "".join(group), None))
                        group.clear()
                    rlist.append(par_elem)
                    expr_flag = False
                else:                             # 上のいずれも当てはまらない場合
                    group.append(par_elem.contents)
            elif par_elem.get_type is Object_tag.BLOCK: # ブロックである場合
                if group:                               # 単語グループがあれば
                    word = "".join(group)
                    rlist.append( parse_element.new(Object_tag.WORD, word, None, None))
                    group.clear()
                rlist.append(par_elem)
                pre_word_is_not_contlol = True
            else:                                       # グループでも未定義でもない場合
                rlist.append(par_elem)
                pre_word_is_not_contlol = True
        return rlist

    def grouping_control_syntax0(self, strlist:list["parse_element"], syntax_strings:list[str]) -> list["parse_element"]:
        # expr<式>の部分を取り出す
        # # これは次の処理で
        # a[<expr>] #要素が1
        # [<expr>,<expr>,...] #要素が1以上 
        # # ここで扱う処理
        # a = <expr>;
        # if <expr> {}
        # for <expt_sub>{}
        # while <expr>{}
        # return <expr>;
        expr_flag0:bool = False # a = <expr>;
        expr_flag1:bool = False # control syntax;
        depth = 0
        control_syntax:str = "" # if , elif ...
        group:list = list()
        rlist:list = list()

        for par_elem in strlist:
            if par_elem.get_type is Object_tag.UNDEF and par_elem.contents == "=" and not expr_flag0:
                # open
                expr_flag0 = True
            elif par_elem.get_type is Object_tag.WORD and par_elem.contents in syntax_strings:
                # open
                if not expr_flag1:
                    control_syntax = par_elem.contents
                depth += 1
            elif par_elem.get_type is Object_tag.UNDEF and par_elem.contents == ";" and expr_flag0:
                # close
                if group:
                    rlist.append(parse_element(Object_tag.EXPR,None,"".join(group),None))
                expr_flag0=False
            elif par_elem.get_type is Object_tag.BLOCK and expr_flag1:
                # close
                depth -= 1
                if group and depth == 0:
                    rlist.append(parse_element(Object_tag.EXPR,None,"".join(group),None))
                    expr_flag1 = False
            else:
                if expr_flag0 or expr_flag1:
                    group.append(par_elem.contents)
                else:
                    rlist.append(par_elem)
        return rlist

    def resolve_control_syntax(self, strlist:list["parse_element"], syntax_string:list[str]) -> list["parse_element"]:
        # resolve_iewfの新しいバージョン
        grouped_strlist = self.grouping_control_syntax(strlist,syntax_string) # とりあえずまとめる

class parse_element:
    # tree状になったparseオブジェクト
    def __init__(self,type_:Object_tag,word:str,expr:"parse_element",contents:"parse_element"):
        self.type_ = type_
        self.word = word
        self.expr = expr
        self.contents = contents

    @classmethod
    def new(cls,type_:Object_tag,word:str,expr:str,contents:"parse_element") -> "parse_element":
        return parse_element(type_,word,expr,contents)

    @property
    def get_type(self):
        return self.type_

    def __repr__(self) -> str:
        return f"type ({self.type_}) expr ({self.expr}) word ({self.word}) contents ({self.contents})\n"

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
    a = Control_parser("")
    code = """
fn add(a:i32,b:i32){
return a+b;
}
fn main ():int{
const list = ["hello","world"];
const string = "world";
for i in list{
const flag = string==i;
if if flag {1} else {0}{
const a = "hello" + "world";
print("hello" + "world");
}}}
"""
    codelist = a.resolve0(code)
    codelist = a.resolve1(codelist)
    print(list(filter(lambda a:not (a.get_type is Object_tag.UNDEF or a.contents==" "),codelist)))

def __test_04():
    a = Control_parser("")
    code = """
const list = [[1,1,1],[0,0,0],[1,1,1]];
const string = "world";
for i in list{
    const flag = string==i;
    if if flag {1} else {0}{
        const a = "hello" + "world";
        print("hello" + "world");
    }
}
"""
    codelist = a.resolve0(code)
    codelist = a.resolve1(codelist)
    print(list(filter(lambda a:not (a.get_type is Object_tag.UNDEF or a.contents==" "),codelist)))


if __name__=="__main__":
    __test_03()
