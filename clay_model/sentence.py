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

    def resolve0(self,code:str) -> list["parse_element"]:
        codelist = self.resolve_quatation(code,self.DOUBLEQUOTATION)
        return codelist

    def resolve1(self,codelist:list["parse_element"]):
        codelist = self.resolve_block(codelist,self.OPENSQUAREBRACKET,self.CLOSESQUAREBRACKET,Object_tag.SQBLOCK)
        codelist = self.resolve_block(codelist,        self.OPENBRACE,        self.CLOSEBRACE,  Object_tag.BLOCK)
        #codelist = self.grouping_word(codelist,["\t","\n"," "],["if","elif","else","white","loop"])
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
                    rlist.append(parse_element.new(object_tag,None,
                        group if object_tag is Object_tag.SQBLOCK else None ,
                        None  if object_tag is Object_tag.SQBLOCK else self.resolve1(group))
                    )
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
    
    def resolve_modifier(self,strlist:list[(Object_tag, str)]) -> list[Object_tag]:
        # ここは文法に直結する、やや面倒な処理になる
        # exprがどこまでなのかを判別する方法をしっかりさせないといけない
        pass #todo

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
                        print(word)
                        rlist.append(parse_element.new(Object_tag.WORD,word, None, None))
                        group.clear()
                    else:                         # なければ
                        rlist.append(par_elem)
                elif par_elem.contents == "=" and pre_word_is_not_contlol:    # "="を見つけたとき、直後に見つけた単語が制御文字でなければ("=="をカウントしてしまう可能性をなくす)
                    if group:                     # 単語グループがあれば
                        word = "".join(group)
                        pre_word_is_not_contlol = word not in control_str
                        print(word)
                        rlist.append(parse_element.new( Object_tag.WORD, word, None, None))
                        group.clear()
                    else:                         # なければ
                        rlist.append(par_elem)
                    expr_flag = True
                elif par_elem.contents == ";" and expr_flag: # ";"を見つけたとき、そして、式フラグが立っているとき
                    if group:                                # 式グループがあれば
                        rlist.append(parse_element.new( Object_tag.EXPR, None, "".join(group), None))
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




    def grouping_control_syntax(self, strlist:list["parse_element"], syntax_strings:list[str]) -> list["parse_element"]:
        # 制御文文字列をまとめる
        rlist = []
        # 制御文字分カウントして、マッチしてからグルーピングまでをまとめる
        flag_counter = 0
        # 選択された文字を先頭に続く単語が文法上特別な意味を持つかどうか調べる
        
        # loop や else の次にはすぐにblockが続く可能性がある。次が文字であれば変数名の一部かもしれないこのことに注意する
        is_syntax = lambda index, syntax_string: all(
                # まずは選択した文字列が全てUNDEFであるかどうかを確認する
                map(
                    lambda a:a.get_type == Object_tag.UNDEF,
                    strlist[index:index + len(syntax_string)]
                )
            ) and syntax_string == "".join(
                map(
                    lambda a:a.contents, # 内容
                    strlist[index:index + len(syntax_string)]
                )
            )

        for index,par_elem in enumerate(strlist):
            contents = par_elem.contents
            type = par_elem.get_type
            if flag_counter > 0:
                pass
            else:
                for matching in syntax_strings:
                    if is_syntax(index,matching):
                        flag_counter = len(matching)
                        rlist.append(parse_element(Object_tag.CONTROL,None,None,matching))
                        break
                else:
                    rlist.append(par_elem)
                    flag_counter = 1
            flag_counter -= 1
        return rlist

    def resolve_control_syntax(self, strlist:list["parse_element"], syntax_string:list[str]) -> list["parse_element"]:
        # resolve_iewfの新しいバージョン
        grouped_strlist = self.grouping_control_syntax(strlist,syntax_string) # とりあえずまとめる

class parse_element:
    # tree状になったparseオブジェクト
    def __init__(self,type_:Object_tag,word:str,expr,contents:"parse_element"):
        self.type_ = type_
        self.contents = contents
        self.expr = expr
        self.word = word

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
list = ["hello","world"];
loop {
    if if string == "{"{
        print("hello world");
    }
}
"""
    # codelist = a.resolve_quatation(code,a.DOUBLEQUOTATION)
    # print(codelist)
    # codelist = a.resolve_block(codelist,a.OPENSQUAREBRACKET,a.CLOSESQUAREBRACKET,Object_tag.SQBLOCK)
    # codelist = a.resolve_block(codelist,a.OPENBRACE,a.CLOSEBRACE,Object_tag.BLOCK)
    # codelist = a.grouping_word(codelist,["\t","\n"," "],["if ","elif ","else ","white ","loop "])
    codelist = a.resolve0(code)
    codelist = a.resolve1(codelist)
    print(codelist)
    # codelist = a.resolve_iewf(codelist,"if ")
    #for i,j in enumerate(codelist):
    #    print(str(i).rjust(2),j)


if __name__=="__main__":
    __test_03()
