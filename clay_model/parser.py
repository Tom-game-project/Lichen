"""
# Lichen parser cray model
Class parser
"""
import copy


class Parser:
    # resolve <expr>
    # 式を解決します
    def __init__(self, code:str) -> None:
        self.code:str = code

        # setting
        ## <, <=, >, >=, !=, <- (python で言うfor i in ...のin)
        ## 左優先リスト
        self.left_priority_list:dict = {
            # 演算子優先順位

            "||":-3,
            "&&":-2,

            "==":0,"!=":0,
            "<":0,">":0,
            "<=":0,">=":0,

            "+":1,"-":1, # prefixの場合は優先順序が変わる

            "*":2,"/":2,
            "%":2,"@":2,
        }
        ## 右優先リスト
        self.right_priority_list:dict = {
            "**":3
        }
        ## 前置修飾 優先リスト
        self.prefix_priority_list:dict = {
            "!": -1
        }
        self.plusminus_prefix_priority = 4
        self.length_order_ope_list:list = sorted((
            self.left_priority_list|\
            self.right_priority_list|\
            self.prefix_priority_list).keys(),
            key=lambda a:len(a))[::-1]
        self.min_priority_operation:int = max((
            self.left_priority_list |\
            self.right_priority_list |\
            self.prefix_priority_list).values()
            )
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

    # grouping methods
    def grouping_elements(self,vec:list,open_char:str,close_char:str,ObjectInstance:"Elem") -> list:
        """
        # grouping_elements 
        grouping block listblock parenblock
        """
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
        ope_chars:str = ''.join(self.left_priority_list.keys()) + ''.join(self.right_priority_list.keys())
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
        if group:
            rlist.append(Word(None,''.join(group)))
            group.clear()
        return rlist
    
    def grouping_syntax(self,vec:list,syntax_words:list[str]) -> list:
        """
        # grouping_syntax
        group "if" "elif" "else" "for" "while" ...
        """
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
    
    def grouping_functioncall(self,vec:list,block,ObjectInstance:"Elem") -> list:
        """
        # grouping_call
        ## group function calls
        ```python
        grouping_call(vec,[Word],Parenblock,Func) -> list:
        ```
        """
        flag:bool = False
        name_tmp:Word = None
        rlist:list = list()
        for i in vec:
            if type(i) is Word:
                if flag:
                    rlist.append(name_tmp)
                name_tmp  = i
                flag = True
            elif type(i) is block:
                if flag:
                    rlist.append(
                        ObjectInstance(
                            name_tmp.get_contents(),# func name
                            self.comma_spliter(i.get_contents()), # args(list[<expr>,..])
                    ))
                    name_tmp = None
                    flag = False
                else:
                    rlist.append(i)
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

    def grouping_list(self,vec:list["Elem"],pre_flag:list,block:"Elem",ObjectInstance:"Elem") -> list:
        """
        ## group list call
        grouping_call(vec,[Word,ListBlock,Func,Syntax],Listblock,List) -> list: 
        返り値があるようなElemについてすべてindexを指定することは可能である
        <List>:
            <name>[<expr>]                     ex) arr[0]
            <Func>[<expr>]                     ex) arr_gen()[0]
            (ListData:[<expr>,...])[<expr>]    ex) [0,1,2][a]
            <syntax> [<expr>]                  ex) if (a){[0,1]}else{[1,0]}[a]
        多次元配列の場合
            <List>[<expr>]                     ex) arr[0][0][0]

        想定される関数の使い方
        ```python
        grouping_list(codelist,[Word,Func,ListBlock,Syntax], ListBlock                 , List) -> list:
        #            (        ,直前にpreflagのいずれか     , 直後にListBlockがあれば   , List) としてまとめる
        ```
        """
        flag:bool = False
        expr:str = None
        group:list = list() # index格納用
        rlist:list = list()
        for i in vec:
            if type(i) is ListBlock: # もし、[]を見つけたなら
                if flag:
                    group.append(i)
                else:
                    expr = i
                    flag = True
            elif any(map(lambda a:type(i) is a,pre_flag)):
                if flag:
                    # すでにflagが立っている場合
                    if group or expr is not None: # something in group or expr
                        rlist += [expr] + group
                        group.clear()
                    else: # group is empty and expr is None
                        pass
                
                expr = i
                flag = True
            else: # flagを下げるべきとき
                if flag:
                    if group:
                        rlist.append(List(expr,copy.copy(group)))
                        expr = None
                        group.clear()
                    else:
                        rlist.append(expr)
                        expr = None
                else:
                    # flagは立っていないとき
                    if group or expr is not None:
                        # list Call かと予想したものの、そうでなかった場合
                        # flag は立っていないけど、groupの中身が存在していて
                        # exprもNoneではない場合
                        rlist += [expr] + group
                        group.clear()
                        expr = None
                    else: # group is empty and expr is None)
                        pass
                flag = False
                rlist.append(i)
        if group or expr is not None:# なにか、残っている場合
            if flag:
                if group:
                    rlist.append(List(expr,copy.copy(group)))
                    expr = None
                    group.clear()
                else:
                    rlist.append(expr)
                    expr = None
            else:
                rlist += [expr] + group
        return rlist

    def find_ope_from_list(self, text:str, ordered_opelist:list[str]) -> str:
        """
        演算子文字列が長い物から順に照会していって検索する
        # return
        str | None
        """
        for i in ordered_opelist:
            if text == i:
                return text
        return None

    def grouping_operator_unit(self,vec:list,ope:str):
        """
        grouping_operatorの中で内部的に使うことを想定しているmethod
        """
        group = list()
        rlist = list()
        ope_size = len(ope)
        for i in vec:
            if not isinstance(i,Elem):
                group.append(i)
                ope_tmp = ''.join(group)
                if len(group) < ope_size:
                    pass
                elif ope_size == len(group):
                    if ope_tmp == ope:
                        rlist.append(Operator(ope))
                    else:
                        rlist += group
                    group.clear()
                else:# ope_size < len(group)
                    rlist += group
                    group.clear()
            else:
                ope_tmp = ''.join(group)
                if len(group) < ope_size:
                    rlist += group
                    group.clear()
                elif ope_size == len(group):
                    if ope_tmp == ope:
                        rlist.append(Operator(ope))
                    else:
                        rlist += group
                    group.clear()
                else:# ope_size < len(group)
                    rlist += group
                    group.clear()
                rlist.append(i)
        return rlist

    def grouping_operator(self,vec:list,ordered_opelist:list[str]):
        """
        # grouping_operator2
        ## 2** -1
        """
        rlist:list = copy.copy(vec)
        for i in ordered_opelist:
            rlist = self.grouping_operator_unit(rlist,i)
        return rlist

    # comma_spliter
    def comma_spliter(self,vec:list) -> "Data":
        """
        # comma_spliter 
        (a,b,c,) == (a,b,c)
        [a,b,c,] == (a,b,c)
        ## 各要素を式として処理する
        """
        group:list = list()
        rlist:list = list()
        for i in vec:
            if i == ',':
                rlist.append(copy.copy(group))
                group.clear()
            else:
                group.append(i)
        if group: # last elements if comma does not exist
            rlist.append(group)
        return rlist

    def code2vec(self,code:str) ->list[str]:
        # クォーテーションをまとめる
        codelist = self.resolve_quotation(code, "\"")
        # ブロック、リストブロック、パレンブロック Elemをまとめる
        for i in self.blocks:codelist = self.grouping_elements(codelist, *i)
        # Wordをまとめる
        codelist = self.grouping_words(codelist, self.split, self.word_excludes)
        ## if, elif, else, forをまとめる
        codelist = self.grouping_syntax(codelist, self.syntax_words)
        ## functionの呼び出しをまとめる
        codelist = self.grouping_functioncall(codelist,ParenBlock,Func)
        ## listの呼び出しをまとめる
        codelist = self.grouping_list(codelist,[Word,Func,ListBlock,Syntax],ListBlock,List)
        
        # TODO:もし配列モードであればここでカンマ区切りの処理をする
        # ここで初めて演算子をまとめる
        # codelist = self.grouping_operator(codelist,self.length_order_ope_list)
        # codelist = self.resolve_operation(codelist)
        codelist = self.comma_spliter(codelist)
        return codelist

    def __find_ope_priority(self,ope:str) -> tuple[str,int]:
        """
        # __find_ope_priority 
        ## このメソッドは、与えられた演算子の優先順序と右優先左優先前置修飾の区別をします
        このメソッドは+,-が前置修飾的に使われていることを判断できない
        """
        if ope in self.left_priority_list:
            return ("left", self.left_priority_list[ope])
        elif ope in self.right_priority_list:
            return ("right", self.right_priority_list[ope])
        elif ope in self.prefix_priority_list:
            return ("prefix",self.prefix_priority_list[ope])
        else:
            raise BaseException("invalid operation")

    def find_min_priority_index(self,vec:list) -> int:
        """
        # find_min_priority
        このメソッドはresolve_operation内で使用すること
        return index of minimum priority
        最も優先順位の低いものを発見する
        ```
        a+b+c
         0 1
        ((a b +) c +)
              0    1
        すなわち、
        (a + b) + c と解釈したいので
        １を見つけたい
        a+b*c
         0
        (a (b c *) +)
        -1+-4
        ((1 -) (4 -) +)
        -42
        (42 -)
        その式の中で最も計算順位の低いものを発見したい
        ```
        # returns 
        最も優先順位の低い演算子のindexを返却する
        """
        priority_tmp:int = self.min_priority_operation + 1 # 最初は優先順位表の最大値 + 1
        index_tmp = None
        for i,j in enumerate(vec):
            if type(j) is Operator:
                contents = j.get_contents()
                # priority_direction : "left"|"right"|"prefix"
                (priority_direction,priority) = self.__find_ope_priority(contents)
                if i - 1 < 0: # 更新
                    index_tmp = i
                    priority_tmp = self.plusminus_prefix_priority
                elif type(vec[i - 1]) is Operator: # jは単項前置演算子
                    pass
                else:
                    if priority < priority_tmp: # 更新
                        index_tmp = i
                        priority_tmp = priority
                    elif priority == priority_tmp:
                        if priority_direction == "left": # 更新
                            index_tmp = i
                            priority_tmp = priority
                        else: # "right" or "prefix"
                            pass
                    else: # priority > priority_tmp
                        pass
            else: # type(j) is not Operator
                pass
        return index_tmp
    
    def find_special_prefix(self):
        """
        # find_special_prefix
        
        """
        pass

    def resolve_operation(self,vec:list) -> list: # 式を計算順序に従い解決するmethodです
        """
        # resolve_operation 
        ここではそれぞれの演算子の優先順序に従い計算を行う
        演算子は引数を２つ取る関数とみなす 1 + 2 -> add(1,2)
        - TODO 2 ** -1のような場合
        ```
        -1**-1**-1
        -(1**-1**-1)
        -(1**(-(1**-1)))
        -(1**(-(1**(-1))))
        ```
        prefix(前置修飾) +,-をどう扱うか
        """
        operation_index:int = self.find_min_priority_index(vec)
        if operation_index is not None: # if operation not found
            pre_group:list = vec[: operation_index]
            post_group:list = vec[operation_index + 1:]
            return [Func(
                vec[operation_index], # operation name (func name)
                [pre_group,post_group]# operation args (func args)
            )]
        else:
            return vec


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

    def resolve_self(self):
        """
        # resolve_self
        それぞれのデータ型で再帰的に処理をする
        """
        print(f"resolve_self 未実装 {type(self).__name__}")
    
    def __repr__(self):return f"<{type(self).__name__} name:({self.name}) contents:({self.contents})>"


## Elements
### basic elements
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

    def resolve_self(self):
        """
        Stringの場合は何もする必要がない
        """
        pass

class ListBlock(Elem):
    """
    リストを格納
    [<expr>,...]
    # returns
    get_contents -> [<expr>,...] # 式集合
    """
    def resolve_self(self):
        expr = self.get_contents()
        parser = Expr_parser(expr)
        self.contents = parser.resolve()

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

    def resolve_self(self):
        expr = self.get_contents()
        parser = Expr_parser(expr)
        self.contents = parser.resolve()

class Word(Elem):# Word Elemは仮どめ
    """
    引数、変数、関数定義、制御文法の文字列
    <word> = fn, let, const, if, while...(exclude: +, -, *, /)
    <word> = <syntax>, <name>, <type>, <Number>
    # returns
    get_contents -> <word>
    """
    def __init__(self, name: str, contents: str) -> None:super().__init__(name, contents)

    def resolve_self(self):
        """
        Wordの場合は何もする必要がない
        """
        pass

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
    # TODO:resolve args
    srgs:[<expr>,...]のような形を期待する
    <name(excludes: 0-9)>(<expr>,...)
    # returns
    get_contents -> (args:[<expr>,...])
    get_name -> (funcname: <name>)
    """
    def __init__(self, name: str, contents: list) -> None:super().__init__(name, contents)


    def resolve_self_unit(self,expr:list):
        parser = Expr_parser(expr)
        return parser.resolve()

    def resolve_self(self):
        args = self.get_contents()
        self.contents = [self.resolve_self_unit(i) for i in args]

    def __repr__(self):
        return f"<{type(self).__name__} func name:({self.name}) args:({self.contents})>"

class List(Elem):
    """
    # List 
    ## index呼び出しは少し複雑である
    
    返り値があるようなElemについてすべてindexを指定することは可能である
    <List>:
        <name>[<expr>]                     ex) arr[0]
        <Func>[<expr>]                     ex) arr_gen()[0]
        (ListData:[<expr>,...])[<expr>]    ex) [0,1,2][a]
        <syntax> [<expr>]                  ex) if (a){[0,1]}else{[1,0]}[a]
    多次元配列の場合
        <List>[<expr>]                     ex) arr[0][0][0]

    # returns
    get_contents -> (index:[<expr,...>])
    get_name -> (listname:<name>)
    """
    def __init__(self, expr: str, index: list[ListBlock]) -> None:
        super().__init__(None, None)
        self.expr = expr
        self.index_list = index

    def __repr__(self):
        return f"<{type(self).__name__} expr:({self.expr}) index:({self.index_list})>"

class Operator(Elem):
    """
    # returns
    get_contents -> ope(ope:["+","-","*","/",...])
    """

    def __init__(self, ope:str) -> None:
        super().__init__(None, ope)
        self.ope = ope

    def __repr__(self):
        return f"<{type(self).__name__} ope:({self.ope})>"

class Data(Elem):
    """
    # Data
    カンマ区切りのデータに対して処理を行います。
    """
    def __init__(self,data:list) -> None:
        super().__init__(None,None)
        self.data:list = data

    def get_data(self):
        return self.data

    def __repr__(self):
        text:str = ""
        for i in self.data:text += repr(i) + ",\n"
        return f"<{type(self).__name__} data:({text})>"

### function declaration
class DecFunc(Elem):
    """
    関数の宣言部分
    (pub) fn <name><parenblock>:<type> <block>
    """
    def __init__(self, funcname:str,args:list,return_type, contents: str) -> None:
        super().__init__(funcname, contents)
        self.return_type = return_type
        self.args = args
    
    def __repr__(self):
        return f"<{type(self).__name__} funcname:({self.name}) args:({self.args}) return type:({self.return_type}) contents:({self.contents})>"

class DecValue(Elem):
    """
    変数の宣言
    (pub)(const|let) <name>:<type> = <expr>;
    """
    def __init__(self, name: str, contents: str) -> None:
        super().__init__(name, contents)
    

class Expr_parser(Parser): # 式について解決します
    """
    # expressions resolver
    ## 式について解決します
    """
    def __init__(self, code: str) -> None:
        super().__init__(code)

    def code2vec(self,code:str) ->list:
        # クォーテーションをまとめる
        codelist = self.resolve_quotation(code, "\"")
        # ブロック、リストブロック、パレンブロック Elemをまとめる
        for i in self.blocks:codelist = self.grouping_elements(codelist, *i)
        # Wordをまとめる
        codelist = self.grouping_words(codelist, self.split, self.word_excludes)
        ## if, elif, else, forをまとめる
        codelist = self.grouping_syntax(codelist, self.syntax_words)
        ## functionの呼び出しをまとめる
        codelist = self.grouping_functioncall(codelist,ParenBlock,Func)
        ## listの呼び出しをまとめる
        codelist = self.grouping_list(codelist,[Word,Func,ListBlock,Syntax],ListBlock,List)
        ## 演算子をまとめる
        codelist = self.grouping_operator(codelist,self.length_order_ope_list)
        ## 演算子を解決する
        codelist = self.resolve_operation(codelist)
        return codelist
    
    def resolve(self):
        codelist = self.code2vec(self.code)
        for i in codelist: # 再帰
            i.resolve_self()
        return codelist


class State_parser(Parser): # 文について解決します
    """
    # statement resolver
    ## 宣言文について解決します
    # ここで解決すべき問題
    TODO 柔軟な型を表現する
    TODO Parenblock内の引数宣言ex) (a:i32,b:i32)
    TODO 変数宣言時の明示的な型宣言 a:Vec<i32>
    """
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.object_type = [
            "i32",
            "i64",
            "f32",
            "f64",
        ]
    
    def grouping_decfunc(self,vec:list) -> list:
        """
        関数宣言部についてまとめます
        (pub) fn <name><parenblock>:<type> <block>
        """
        flag:bool = False
        group:list = list()
        rlist:list = list()
        for i in vec:
            pass
        return rlist
