from enum import Enum,auto

# debug tools
from pprint import pprint
import logging
import copy


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


class Expr_parser:
    # resolve <expr>
    # 式を解決します
    def __init__(self, code:str, mode = "lisp") -> None:
        self.code:str = code
        self.mode = mode

        # setting
        ## <, <=, >, >=, !=, <- (python で言うfor i in ...のin)
        self.rankinglist:dict = {
            # 演算子優先順位
            "&&":-1,"||":-1,

            "==":0,"!=":0,
            "<":0,">":0,
            "<=":0,">=":0,

            "+":1,"-":1,

            "*":2,"/":2,
            "%":2,"@":2,

            "^":3,"**":3
        }
        # TODO: 前置修飾(prefix)たとえば!(not)を解決する必要がある
        self.length_order = sorted(self.rankinglist.keys(),key=lambda a:len(a))[::-1]
        self.blocks = [
            ('{','}',Block),
            ('[',']',ListBlock),
            ('(',')',ParenBlock),
        ]
        self.split = [' ', '\t','\n']
        self.word_excludes = [';',':',',']
        self.syntax_words = [
            "if",
            "elif",
            "else",
            "loop",
            "for",
            "while"
        ]
        # const
        self.ESCAPESTRING = "\\"
    # expr range checker
    def expr_range_cheacker(self):
        pass

    # クォーテーションはまとまっている前提
    def resolve_quotation(self,code:str,quo_char:str) -> list[str]:
        # クォーテーションをまとめる
        open_flag:bool = False
        escape_flag:bool = False
        rlist:list = list()
        group:list = list()
        newline_counter :int = 0
        column_counter:int = 0
        for inner in code:
            if inner == "\n":
                column_counter = 0
                newline_counter += 1
            else:
                column_counter += 1

            if escape_flag:
                group.append(inner)
                escape_flag = False
            else:
                if inner == quo_char:
                    if open_flag:
                        group.append(inner)
                        rlist.append(
                            String(None,"".join(group))
                        )
                        group.clear()
                        open_flag = False
                    else:
                        group.append(inner)
                        position = (newline_counter,column_counter)
                        open_flag = True
                else:
                    if open_flag:
                        if inner == self.ESCAPESTRING:
                            escape_flag = True
                        else:
                            escape_flag = False
                        group.append(inner)
                    else:
                        rlist.append(inner)
        return rlist

    # grouping functions
    def grouping_elements(self,vec:list,open_char:str,close_char:str,ObjectInstance:"Elem") -> list:
        rlist:list[str] = list()
        group:list[str] = list()
        depth:int = 0

        for i in vec:
            if i == open_char:
                if depth > 0:
                    group.append(i)
                elif depth == 0:
                    pass
                else:
                    print("Error!")
                    return
                depth += 1
            elif i == close_char:
                depth -= 1
                if depth > 0:
                    group.append(i)
                elif depth == 0:
                    rlist.append(ObjectInstance(None,copy.copy(group)))
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

    def grouping_words(self,vec:list,split:list[str],excludes:list[str]) -> list[str]:
        """
        # wordを切り出すメソッド
        
        - すでにElem に到達したらその時点で区切る
        - 区切り文字に到達したら区切る(/*例えば*/ 区切り文字: '\t', ' ', '\n')
        - 演算子に使用されている文字であれば区切る
        """
        rlist:list = list()
        group:list = list()
        ope_chars:str = ''.join(self.rankinglist.keys())
        ope_chars = ope_chars + ''.join(excludes)
        for i in vec:
            if isinstance(i,Elem):# Elemクラスを継承しているかどうか調べる
                # すでにrole決定済み
                if group:
                    rlist.append(Word(None,''.join(group)))
                    group.clear()
                rlist.append(i)
            elif i in split:
                # 区切り文字
                if group:
                    rlist.append(Word(None,''.join(group)))
                    group.clear()
            elif i in ope_chars:
                if group:
                    rlist.append(Word(None,''.join(group)))
                    group.clear()
                rlist.append(i)
            else:
                group.append(i)
        return rlist
    
    def grouping_syntax(self,vec:list,syntax_words:list[str]) -> list:
        flag:bool = False
        group:list = list()
        rlist:list = list()
        for i in vec:
            if type(i) is Word:
                if i.get_contents() in syntax_words:
                    group.append(i)
                    flag = True
                else:
                    rlist.append(i)
            elif type(i) is ParenBlock:
                if flag:
                    group.append(i)
                else:
                    rlist.append(i)
            elif type(i) is Block:
                if flag:
                    group.append(i)
                    if len(group) == 2:
                        name: Word= group[0]
                        block: Block = group[1]
                        rlist.append(
                            Syntax(
                                name.get_contents(),
                                None,
                                block.get_contents()
                            )
                        )
                    elif len(group) == 3:
                        name:Word=group[0]
                        paren:ParenBlock = group[1]
                        block:Block = group[2]
                        rlist.append(
                            Syntax(
                                name.get_contents(),
                                paren.get_contents(),
                                block.get_contents()
                            )
                        )
                    else:
                        print("ここでError!",group)
                        return
                    group.clear()
                    flag = False
                else:
                    rlist.append(i)
            else:
                rlist.append(i)
        return rlist
    
    def grouping_function(self,vec:list) -> list:
        flag:bool = False
        name_tmp:Word = None
        rlist:list = list()
        for i in vec:
            if type(i) is Word:
                name_tmp  = i
                flag = True
            elif type(i) is ParenBlock:
                if flag:
                    rlist.append(
                        Func(
                            name_tmp.get_contents(),# func name
                            i.get_contents(),       # args
                    ))
                    name_tmp = None
                    flag = False
            else:
                if flag:
                    rlist.append(name_tmp)
                    rlist.append(i)
                    flag = False
                    name_tmp = None
                else:
                    rlist.append(i)
        if flag:
            rlist.append(name_tmp)
        return rlist

    def is_number(self,text:str) -> bool:
        size = len(text)
        for i,j in enumerate(text):
            if i == 0 and j=='.':
                # ex) .141592
                return False
            if i == size - 1 and j=='.':
                # ex) 3.
                return False
            elif '0' <= j <= '9':
                pass
            else:
                return False
        return True

    def split_symbol(self,vec:list[str]) -> list[str]:
        pass

    def code2vec(self,code:str) ->list[str]:
        # クォーテーションをまとめる
        codelist = self.resolve_quotation(code, "\"")
        # ブロック、リストブロック、パレンブロック Elemをまとめる
        for i in self.blocks:codelist = self.grouping_elements(codelist, *i)
        # Wordをまとめる
        codelist = self.grouping_words(codelist, self.split, self.word_excludes)
        codelist = self.grouping_syntax( codelist, self.syntax_words)
        codelist = self.grouping_function(codelist) 
        # codelist = self.split_symbol(codelist)
        return codelist


class Expr_element:
    def __init__(self, name:str, type_:str, args:list, mode="expr") -> None:
        self.mode = mode
        self.name:str = name
        self.args:list = args
        self.type_ = type_

    def __getitem__(self, key):
        return self.args[key]

    def __repr__(self) -> str:
        if self.mode == "lisp":
            return f"({self.name} {' '.join(map(lambda a:str(a) if type(a) is str else repr(a),self.args))})"
        elif self.mode == "PM":
            return f"({' '.join(map(repr,self.args))} {self.name})"
        return f"({' '.join(map(repr,self.args))} {self.name})"


# Base Elem
class Elem:
    """
    字句解析用データ型
    """
    def __init__(self, name:str, contents:str) -> None:
        self.name = name
        self.contents = contents

    def get_contents(self):return self.contents

    def get_name(self):return self.name
    
    def __repr__(self):return f"<{type(self).__name__} name:({self.name}) contents:({self.contents})>"


# Elements
class Block(Elem):
    """
    処理集合を格納
    <block> = {
        <proc>
    }
    <proc> = <expr> ;...
    # returns
    get_contents -> <proc>
    """
    def __init__(self, name: str, contents: str) -> None:super().__init__(name, contents)

class String(Elem):
    """
    文字列を格納
    "<string>"
    '<char>'
    # returns
    get_contents -> <string> or <char>
    """
    def __init__(self, name: str, contents: str) -> None:super().__init__(name, contents)

class ListBlock(Elem):
    """
    リストを格納
    [<expr>,...]
    # returns
    get_contents -> [<expr>,...] # 式集合
    """
    def __init__(self, name: str, contents: str) -> None:super().__init__(name, contents)

class ParenBlock(Elem):
    """
    式ブロック
    または
    関数の引数宣言部
    (<expr>,...)
    or
    (<dec>,...)
    <dec> = <word>:<type>
    # returns
    get_contents -> <expr>,... # 式集合 式の範囲で宣言集合になることはない
    """
    def __init__(self, name: str, contents: str) -> None:super().__init__(name, contents)

class Word(Elem):# Word Elemは仮どめ
    """
    引数、変数、関数定義、制御文法の文字列
    <word> = fn, let, const, if, while...(exclude: +, -, *, /)
    <word> = <syntax>, <name>, <type>, <Number>
    # returns
    get_contents -> <word>
    """
    def __init__(self, name: str, contents: str) -> None:super().__init__(name, contents)

class Syntax(Elem):
    """
    # returns
    <syntax> = if, elif, else, loop, for, while
    get_name ->  if, elif, else, loop, for, while
    get_expr -> <expr>
    get_contents -> {<proc>}
    """ 
    def __init__(self, name: str, expr, contents) -> None:
        super().__init__(name, contents)
        self.expr = expr

    def get_expr(self):
        return self.expr
    
    def __repr__(self):
        # override
        return f"<{type(self).__name__} name:({self.name}) expr:({self.expr}) contents:({self.contents})>"

class Func(Elem):
    """
    <name(excludes: 0-9)>(<expr>,...)
    # returns
    get_contents -> (srgs:[<expr>,...])
    get_name -> (funcname: <name>)
    """
    def __init__(self, name: str, contents: str) -> None:super().__init__(name, contents)

    def __repr__(self):
        return f"<{type(self).__name__} func name:({self.name}) args:({self.contents})>"


# Proc_parser
class Proc_parser:
    # resolve <proc>
    # 処理を解決します
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

    def resolve0(self,code:str) -> list["proc_element"]:
        codelist = self.resolve_quatation(code,self.DOUBLEQUOTATION)
        return codelist

    def resolve1(self,codelist:list["proc_element"]) -> list["proc_element"]:
        codelist = self.resolve_block(codelist) # {}
        codelist = self.resolve_block2(codelist)
        return codelist

    def resolve2(self,codelist:list["proc_element"]):
        return codelist

    def resolve_quatation(self,strlist:list[str], quo_char:str) -> list["proc_element"]:
        # クォーテーションをまとめる
        open_flag:bool = False
        escape_flag:bool = False
        rlist:list = list()
        group:list = list()
        newline_counter :int = 0
        column_counter:int = 0
        for inner in strlist:
            if inner == "\n":
                column_counter = 0
                newline_counter += 1
            else:
                column_counter += 1

            if escape_flag:
                group.append(inner)
                escape_flag = False
            else:
                if inner == quo_char:
                    if open_flag:
                        #group.append(i)
                        rlist.append(
                            proc_element.new(Object_tag.STRING,None,None,"".join(group),position,len(group))
                        )
                        group.clear()
                        open_flag = False
                    else:
                        #group.append(i)
                        position = (newline_counter,column_counter)
                        open_flag = True
                else:
                    if open_flag:
                        if inner == self.ESCAPESTRING:
                            escape_flag = True
                        else:
                            escape_flag = False
                        group.append(inner)
                    else:
                        rlist.append(
                            proc_element.new(Object_tag.UNDEF,None,None,inner,(newline_counter,column_counter),1)
                        ) # undefのときはそのまま
        return rlist

    # ブロックごとにまとめる
    def resolve_block(self,strlist:list["proc_element"]) -> list["proc_element"]:
        depth:int = 0
        rlist:list = list()
        group:list = list()
        for par_elem in strlist:
            inner = par_elem.contents
            elem_type_tag = par_elem.get_type

            if elem_type_tag is Object_tag.UNDEF and inner == "{":
                if depth>0:
                    group.append(par_elem)
                elif depth == 0:
                    #group.append(i)
                    position = par_elem.position
                    pass
                else:
                    print("Error!")
                    return
                depth += 1
            elif elem_type_tag is Object_tag.UNDEF and inner == "}":
                depth -= 1
                if depth > 0:
                    group.append(par_elem)
                elif depth == 0:
                    #group.append(i)
                    contents = self.resolve1(group)
                    contents_length = sum(map(lambda a:a.length,contents))
                    rlist.append(
                        proc_element(Object_tag.BLOCK,None,None,contents,position,contents_length + 2)
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

    def resolve_block2(self,strlist:list["proc_element"]):

        depth:int = 0
        group = list()
        rlist = list()
        position:tuple[int,int]
        for par_elem in strlist:
            inner = par_elem.contents
            elem_type_tag = par_elem.get_type
            if elem_type_tag is Object_tag.UNDEF and inner == "(":
                if depth > 0:
                    group.append(par_elem)
                elif depth == 0:
                    position = par_elem.position
                else:
                    print("Error!")
                    return
                depth += 1
            elif elem_type_tag is Object_tag.UNDEF and inner == ")":
                depth -= 1
                if depth > 0:
                    group.append(par_elem)
                elif depth == 0:
                    contents = group # 工事中
                    contents_length = sum(map(lambda a:a.length,contents))
                    if group:
                        rlist.append(proc_element.new(
                            type_ = Object_tag.PARENBLOCK,
                            word = None,
                            expr = copy.copy(contents),
                            contents = None,
                            position = position,
                            length = contents_length
                        ))
                        group.clear()
                else:
                    print("Error!")
                    return
            else:
                if depth>0:
                    group.append(par_elem)
                elif depth == 0:
                    rlist.append(par_elem)
                else:
                    print("Error!")
                    return
        return rlist

    def grouping_word(self,strlist:list["proc_element"], split_str:str, control_str:str) -> list["proc_element"]:
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

        for par_elem in strlist:
            # strlistはすでに、文字列ブロックへとグループされている
            if par_elem.get_type is Object_tag.UNDEF: # タイプが未定義であった場合
                if par_elem.contents in split_str: # 区切り文字であった場合
                    if group:                     # もし単語グループがあれば
                        word = "".join(group)
                        rlist.append(proc_element.new(Object_tag.WORD,word, None, None))
                        group.clear()
                    else:                         # なければ
                        rlist.append(par_elem)
                else:                             # 上のいずれも当てはまらない場合
                    group.append(par_elem.contents)
            elif par_elem.get_type is Object_tag.BLOCK: # ブロックである場合
                if group:                               # 単語グループがあれば
                    word = "".join(group)
                    rlist.append( proc_element.new(Object_tag.WORD, word, None, None))
                    group.clear()
                rlist.append(par_elem)
            else:                                       # グループでも未定義でもない場合
                rlist.append(par_elem)
        return rlist

    def grouping_control_syntax0(self, strlist:list["proc_element"], syntax_strings:list[str]) -> list["proc_element"]:
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
                    rlist.append(proc_element(Object_tag.EXPR,None,"".join(group),None))
                expr_flag0=False
            elif par_elem.get_type is Object_tag.BLOCK and expr_flag1:
                # close
                depth -= 1
                if group and depth == 0:
                    rlist.append(proc_element(Object_tag.EXPR,None,"".join(group),None))
                    expr_flag1 = False
            else:
                if expr_flag0 or expr_flag1:
                    group.append(par_elem.contents)
                else:
                    rlist.append(par_elem)
        return rlist

    def resolve_control_syntax(self, strlist:list["proc_element"], syntax_string:list[str]) -> list["proc_element"]:
        # resolve_iewfの新しいバージョン
        grouped_strlist = self.grouping_control_syntax0(strlist,syntax_string) # とりあえずまとめる


class proc_element:
    # tree状になったparseオブジェクト
    def __init__(self,type_:Object_tag,word:str,expr:"proc_element",contents:"proc_element",position:tuple[int,int],length:int):
        # position (ln,col)
        self.type_ = type_
        self.word = word
        self.expr = expr
        self.contents = contents
        self.position = position
        self.length = length

    @classmethod
    def new(cls,type_:Object_tag,word:str,expr:str,contents:"proc_element",position:tuple[int,int],length:int) -> "proc_element":
        return proc_element(type_,word,expr,contents,position,length)

    @property
    def get_type(self):
        return self.type_

    def __repr__(self) -> str:
        return f"type ({self.type_}) expr ({self.expr}) word ({self.word}) contents ({self.contents}) (Ln: {self.position[0]},col: {self.position[1]})\n"

# test

def __test_00():
    a = Proc_parser("")
    with open("../examples/ex02.lc",mode="r",encoding="utf-8") as f:
        code = f.read()
    codelist = a.resolve0(code)
    codelist = a.resolve1(codelist)
    #print(list(map(lambda b:"<BLOCK>" if b.get_type is Object_tag.BLOCK else b,codelist)))
    print(codelist)

def __test_01():
    a = Proc_parser("")
    code = """
const list = [[1,1,1],[0,0,0],[1,1,1]];
const string = "world";
for (i <- list){
    const flag = string==i;
    if (if (flag){1} else {0}){
        const a = "hello" + "world";
        print("hello" + "world");
    };
};
"""
    codelist = a.resolve0(code)
    codelist = a.resolve1(codelist)
    print(list(filter(lambda a:not (a.get_type is Object_tag.UNDEF or a.contents==" "),codelist)))

def __test_02():
    a = Expr_parser("")
    # expr test cases
    test_cases:list = list()
    with open("../examples/ex03.lc") as f :test_cases = [i for i in f]
    # print(test_cases)
    for testcase in test_cases:
        codelist = a.resolve_quotation(testcase,"\"")
        codelist = a.resolve_quotation(codelist,"'")
        for i in [
            ('{','}',Block),
            ('[',']',ListBlock),
            ('(',')',ParenBlock)]:
            codelist = a.grouping_elements(codelist,*i)
        print(testcase,codelist)
        print()

def __test_03():
    a = Expr_parser("")
    # expr test cases
    test_cases:list = list()
    with open("../examples/ex03.lc") as f :test_cases = [i for i in f]
    # print(test_cases)
    for testcase in test_cases:
        codelist = a.code2vec(testcase)
        pprint(codelist)
        print()

def __test_04():
    a = Expr_parser("")
    # expr test cases
    with open("../examples/ex03.lc") as f :test_cases = [i for i in f]
    # print(test_cases)
    testcase = test_cases[3]
    codelist = a.code2vec(testcase)
    print(testcase,codelist)
    print()


if __name__=="__main__":
    __test_03()
