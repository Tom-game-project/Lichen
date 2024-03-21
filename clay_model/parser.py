"""
# Lichen parser cray model
Class parser

TODO : コメントをかけるようにする

"""
import copy


class Parser:
    # resolve <expr>
    # 式を解決します
    def __init__(self, code:str,depth = 0) -> None:
        self.code:str = code
        self.depth = depth

        # setting
        ## <, <=, >, >=, !=, <- (python で言うfor i in ...のin)
        ## =, +=, -=, *=, /= 演算子として扱う
        ## TODO : 優先度リストの実装きれいに書き直す
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
            # 最下位
            "=":-4,
            "+=":-4,
            "-=":-4,
            "*=":-4,
            "/=":-4,
            # 二乗
            "**":3,
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
        self.FUNCTION = "fn"
        self.SEMICOLON = ";"
        
        # State_parser
        ##
        self.control_statement = [
            "return",
            "break",
            "continue",
            "assert",
        ]
        ## object type
        self.object_type = [
            "i32",
            "i64",
            "f32",
            "f64",
        ]
        self.value_dec_mutable = [
            "const",
            "let"
        ]
        self.expr_excludes:list = [
            DecFunc, # 関数宣言部分
            DecValue, # 変数、定数宣言部分
            ControlStatement # 制御文法部分
        ]

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
                            String(None,"".join(group),self.depth)
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
                    rlist.append(ObjectInstance(None,copy.copy(group),self.depth))
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
                    rlist.append(Word(None,''.join(group),self.depth))
                    group.clear()
                rlist.append(i)
            elif i in split:
                # 区切り文字
                if group:
                    rlist.append(Word(None,''.join(group),self.depth))
                    group.clear()
            elif i in ope_chars:
                if group:
                    rlist.append(Word(None,''.join(group),self.depth))
                    group.clear()
                rlist.append(i)
            else:
                group.append(i) 
        if group:
            rlist.append(Word(None,''.join(group),self.depth))
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
                                block.get_contents(),
                                self.depth
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
                                block.get_contents(),
                                self.depth
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
                            self.depth
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
                        rlist.append(List(expr,copy.copy(group),self.depth))
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
                    rlist.append(List(expr,copy.copy(group),self.depth))
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
                        rlist.append(Operator(ope,self.depth))
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
                        rlist.append(Operator(ope,self.depth))
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
                [pre_group,post_group],# operation args (func args)
                self.depth
            )]
        else:
            return vec

    def resolve(self):
        return self.code2vec(self.code)

    def __resolve_func_arg_unit(self,code:list):
        codelist = self.grouping_words(code, self.split, self.word_excludes)
        return codelist

    def resolve_func_arg(self):
        """
        # resolve_func_arg
        関数の引数の解決
        """
        rlist:list = list()
        for i in self.code:
            rlist.append(self.__resolve_func_arg_unit(i))
        return rlist

# Base Elem
class Elem:
    """
    字句解析用データ型
    """
    def __init__(self, name:str, contents:str,depth:int) -> None:
        self.name = name
        self.contents = contents
        self.depth = depth

    def get_contents(self):return self.contents

    def get_name(self):return self.name

    def wat_format_gen(self):
        """
        # wat_format_gen

        """
        print("未実装")
        return "まだ実装できてないよ〜"

    def resolve_self(self):
        """
        # resolve_self
        それぞれのデータ型で再帰的に処理をする
        """
        print(f"resolve_self 未実装 {type(self).__name__}")

    def __repr__(self):
        return f"<{type(self).__name__} depth:({self.depth}) name:({self.name}) contents:({self.contents})>"

    def show(self):
        """
        # show
        TODO 
        階層構造を見やすく表示します
        """
        return " "*self.depth + f"""<{type(self).__name__} name:({self.name})
contents:({self.contents})>"""
    
    def get_all_local_value(self):
        """
        # get_all_local_value
        持たない場合は空リストを返却する
        """
        print(f"{type(self).__name__} get_all_local_value 未実装")
        return []

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
    def __init__(self, name: str, contents: str, depth:int) -> None:super().__init__(name, contents,depth)

    def resolve_self(self):
        state_parser = State_parser(self.contents, depth = self.depth + 1)
        self.contents = state_parser.resolve()

    def get_all_local_value(self) -> list[Elem]:
        rlist:list = list()
        for i in self.contents:
            # ローカル変数を含んだリスト
            local_vlaue:list = i.get_all_local_value()
            rlist += local_vlaue
        return rlist

class String(Elem):
    """
    文字列を格納
    "<string>"
    '<char>'
    # returns
    get_contents -> <string> or <char>
    """
    def __init__(self, name: str, contents: str, depth: int) -> None:
        super().__init__(name, contents, depth)

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
    def resolve_self_unit(self,expr):
        expr_parser = Expr_parser(expr)
        return expr_parser.resolve()

    def resolve_self(self):
        expr = self.get_contents()
        parser = Parser(expr, depth = self.depth + 1)
        self.contents = [self.resolve_self_unit(i) for i in parser.resolve()]

    def __init__(self, name: str, contents: str, depth: int) -> None:
        super().__init__(name, contents, depth)

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
    def __init__(self, name: str, contents: str, depth: int) -> None:
        super().__init__(name, contents, depth)

    def resolve_self(self):
        expr = self.get_contents()
        parser = Expr_parser(expr, depth = self.depth + 1)
        self.contents = parser.resolve()

    def wat_format_gen(self):
        """
# wat_format_gen
このmethodが呼び出されるときselfは
式の優先順位変更に使用するParenBlockであることに注意
        """
        return self.contents[0].wat_format_gen()

class Word(Elem):# Word Elemは仮どめ
    """
    引数、変数、関数定義、制御文法の文字列
    <word> = fn, let, const, if, while...(exclude: +, -, *, /)
    <word> = <syntax>, <name>, <type>, <Number>
    # returns
    get_contents -> <word>
    """
    def __init__(self, name: str, contents: str, depth: int) -> None:
        super().__init__(name, contents, depth)

    def resolve_self(self):
        """
        Wordの場合は何もする必要がない
        """
        pass

    def __self_is_i32(self) -> bool:
        """
# self_is_i32
自分自身がi32であった場合、Trueを返却
        """
        for i in self.contents:
            if '0' <= i <= '9':
                pass
            else:
                return False
        return True
    
    def wat_format_gen(self):
        """
# wat_format_gen
## TODO:数字ではない場合
        """
        if self.__self_is_i32():
            return "i32.const {}\n".format(self.contents)
        else:
            return "local.get ${}\n".format(self.contents)

class Syntax(Elem):
    """
    # returns
    <syntax> = if, elif, else, loop, for, while
    get_name ->  if, elif, else, loop, for, while
    get_expr -> <expr>
    get_contents -> {<proc>}
    """ 
    def __init__(self, name: str, expr, contents, depth:int) -> None:
        super().__init__(name, contents, depth)
        self.expr = expr

    def get_expr(self):
        return self.expr
    
    def resolve_self(self):
        """
        # resolve_self
        ## if while for loop などを解決する
        """
        state_parser = State_parser(self.contents, depth = self.depth + 1)
        self.contents = state_parser.resolve()
        # expr は Noneである可能性があることに注意
        if self.expr is not None:
            expr_parser = Expr_parser(self.expr, depth = self.depth + 1)
            self.expr = expr_parser.resolve()
        else:
            pass

    def __repr__(self):
        # override
        return f"<{type(self).__name__} depth:({self.depth}) name:({self.name}) expr:({self.expr}) contents:({self.contents})>"

    def get_all_local_value(self):
        rlist:list = list()
        for i in self.contents:
            local_value = i.get_all_local_value()
            rlist += local_value
        return rlist

class SyntaxBox(Elem):
    """
    # SyntaxBox
    if elif else,loop else,while elseなどの連続して解釈されるコードを集めます
    
    """
    def __init__(self, name: str, contents: list[Syntax], depth:int) -> None:
        super().__init__(name, contents, depth)

    def resolve_self(self):
        """
        listの各要素は、すべてSyntaxになっているはずなので、
        それぞれのsyntax要素のresolve_self methodを呼び出せば良い
        ここではparserを呼び出さないのでdepthを深くしない
        """
        for i in self.contents:
            i.resolve_self()

    # def __repr__(self):
    #     return f"<{type(self).__name__} name:({self.name}) args:({self.contents})>"

    def get_all_local_value(self):
        rlist:list = list()
        for i in self.contents:
            local_value = i.get_all_local_value()
            rlist += local_value
        return rlist

class Func(Elem):
    """
    # TODO:resolve args
    srgs:[<expr>,...]のような形を期待する
    <name(excludes: 0-9)>(<expr>,...)
    # returns
    get_contents -> (args:[<expr>,...])
    get_name -> (funcname: <name>)
    """
    def __init__(self, name: str, contents: list, depth:int) -> None:
        super().__init__(name, contents, depth)
        self.ope_correspondence_table = {
            # https://developer.mozilla.org/en-US/docs/WebAssembly/Reference/Numeric
            "+":"i32.add", # add
            "-":"i32.sub", # sub 
            "*":"i32.mul", # mul
            "/":"i32.div_u",# div
            "%":"i32.rem_u", # mod 

            "==":"i32.eq",# Equal
            "!=":"i32.ne",# Not equal 
            "<":"i32.lt_u",# Less than
            ">":"i32.gt_u", # greater than
            "<=":"i32.le_u", # Less or equal
            ">=":"i32.ge_u", # greater or equal

            "&&":"i32.and", # and
            "||":"i32.or", # or

            # TODO
            "=":"local.set"
        }
    
    def wat_format_gen(self) -> str:
        """
        # wat_format_gen
        """
        wasm_code = ""
        call_name:str = None
        if type(self.name) is Operator:
            if self.name.get_contents() == '=':
                # "=", "+="などの特殊な場合 
                if len(self.contents) == 2:
                    for i in self.contents[1:]:# 0番目を飛ばす
                        if len(i) == 0:        # TODO
                            pass
                        else:
                            wasm_code += i[0].wat_format_gen()
                    # 以下の一行で`self.contents[0][0]`は必ずWordオブジェクトにならなければいけない
                    wasm_code += "local.set ${}\n".format(self.contents[0][0].get_contents())
                else:
                    # error
                    # a = b
                    # かならず引数は2つになるはずなのでそれ以外の場合はError!
                    raise BaseException("Error!")
            else:
                # 普通の演算子(代入やincrではない)場合
                call_name = self.ope_correspondence_table[self.name.get_contents()]
                for i in self.contents: # per arg
                    if len(i) == 0:        # TODO
                        pass
                    else:
                        wasm_code += i[0].wat_format_gen()
                wasm_code += call_name + '\n'
        elif type(self.name) is str:
            for i in self.contents: # per arg
                if len(i) == 0:        # TODO
                    pass
                else:
                    wasm_code += i[0].wat_format_gen()
            wasm_code += "call ${}\n".format(self.name)
        else:
            pass
        return wasm_code

    def resolve_self_unit(self,expr:list):
        parser = Expr_parser(expr, depth = self.depth + 1)
        return parser.resolve()

    def resolve_self(self):
        args = self.get_contents()
        self.contents = [self.resolve_self_unit(i) for i in args]

    # def __repr__(self):
    #     return f"<{type(self).__name__} func name:({self.name}) args:({self.contents})>"

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
    def __init__(self, expr: str, index: list[ListBlock],depth:int) -> None:
        super().__init__(None, None, depth)
        self.expr = expr
        self.index_list = index

    def resolve_self_unit(self,expr):
        expr_parser = Expr_parser(expr, depth = self.depth + 1)
        return expr_parser.resolve()

    def resolve_self(self):
        """
        # resolve_self 
        ## 処理前
        ```
        index_list = [<ListBlock>,...]
        ```
        ## 処理後
        ```
        index_list = [<expr>,<expr>]
        ```
        """
        self.index_list = [self.resolve_self_unit(i.get_contents()) for i in self.index_list]

    def __repr__(self):
        return f"<{type(self).__name__} depth:({self.depth}) expr:({self.expr}) index:({self.index_list})>"

class Operator(Elem):
    """
    # returns
    get_contents -> ope(ope:["+","-","*","/",...])
    """

    def __init__(self, ope:str, depth:int) -> None:
        super().__init__(None, ope, depth)
        self.ope = ope

    def __repr__(self):
        return f"<{type(self).__name__} depth:({self.depth}) ope:({self.ope})>"

class Data(Elem):
    """
    # Data
    カンマ区切りのデータに対して処理を行います。
    """
    def __init__(self,data:list, depth:int) -> None:
        super().__init__(None, None, depth)
        self.data:list = data

    def get_data(self):
        return self.data

    def __repr__(self):
        text:str = ""
        for i in self.data:text += repr(i) + ",\n"
        return f"<{type(self).__name__} depth:({self.depth}) data:({text})>"

class Arg(Elem):
    """
    # ArgParse
    ## 引数エレメント
    """
    def __init__(self, name: str, type_: str, depth:int) -> None:
        super().__init__(name, type_, depth)

### function declaration
class DecFunc(Elem):
    """
    関数の宣言部分
    (pub) fn <name><parenblock>:<type> <block>
    args
    TODO:decfunc内で使用するローカル変数をすべて取得するメソッドを作成する
    """
    def __init__(self, funcname:str,args:list,return_type, contents: Block,pub_flag:bool, depth:int) -> None:
        super().__init__(funcname, contents, depth)
        self.return_type = return_type
        self.args = args
        self.pub_flag  = pub_flag

    def arg_parse(self,args_list:list[list]) -> list[Arg]:
        """
        # arg_parse
        [[<word>,":",<word>],[<word>,":",<word>]]
        このような形のリスト
        """
        rlist:list = list()
        for i in args_list:
            flag:bool = False
            name = None
            type_ = None
            for j in i:
                if j == ":":
                    flag = True
                elif flag:
                    # type
                    type_ = j.get_contents()
                else:
                    # name
                    name = j.get_contents()
            rlist.append(Arg(name,type_))
        return rlist

    def wat_format_gen(self) -> str:
        """
# wat_format_gen

## DecFunc
        ```wat
(func $name
(param $b i32);;引数
(param $a i32)
(result i32)
;;処理
)
        ```
        """
        wasm_code = ""
        funcname:str = self.name
        args:list[Arg] = self.arg_parse(self.args)
        r_type = self.return_type
        wasm_code += "(func ${}\n".format(funcname) # open func    
        for i in args:
            wasm_code += "(param ${} {})\n".format(i.get_name(),i.get_contents())
        wasm_code += "(resulut {})\n".format(r_type[0].get_contents())
        # TODO : ここに処理を書く
        wasm_code += ")\n" # close func
        return wasm_code

    def resolve_self(self):
        """
        # resolve_self
        # TODO argsのtypeの処理
        """
        parser = Parser(self.args, depth = self.depth + 1)
        self.args = parser.resolve_func_arg()
        self.contents.resolve_self()

    def __repr__(self): # public 関数のときの表示
        return f"<{type(self).__name__} depth:({self.depth}) pubflag({self.pub_flag}) funcname:({self.name}) args:({self.args}) return type:({self.return_type}) contents:({self.contents})>"

    def get_all_local_value(self) -> list:
        """
        # get_all_local_value
        decfunc内で使用するローカル変数をすべて取得するメソッドを作成する
        decvalueのリスト
        """
        rlist:list = list()
        # error check
        if type(self.contents) is Block:
            #print ("decfunc".center(50,'='))
            pass
        else:
            print ("Error! : function contetns is not Block")
        return self.contents.get_all_local_value()


class DecValue(Elem):
    """
    変数の宣言
    (pub) (const|let) <name>:<type> = <expr>;
    ## returns
    get_name() -> valuename (宣言した)変数の名前
    get_content() -> 宣言の具体的な内容
    関数の宣言は代入とセットの場合がある
    """
    def __init__(self,mutable:str, valuename: str, type_:str, contents:list, depth:int, pub_flag = False) -> None:
        super().__init__(
            valuename, # 宣言した変数(または定数)名
            contents,   # 初期化式、Noneの場合もある
            depth
        )
        self.mutable = mutable# const or let
        self.type_ = type_ # 変数(または定数)の型
        self.pub_flag = pub_flag # publicであるかどうか

    def get_type(self):
        return self.type_
    
    def resolve_self(self):
        """
        # resolve_self
        初期化式がある場合それを解決します
        """
        if self.contents is not None:
            expr_parser = Expr_parser(self.contents, depth = self.depth + 1)
            self.contents = expr_parser.resolve()
        else:
            pass

    def __repr__(self): # public 関数のときの表示
        return f"<{type(self).__name__} depth:({self.depth}) pubflag:({self.pub_flag}) {self.mutable} value_name:({self.name}) value_type({self.type_}) contents:({self.contents})>"

    def get_all_local_value(self):
        rlist:list = list()
        if self.contents is not None:
            for i in self.contents:
                local_value = i.get_all_local_value()
                rlist += local_value
        rlist += [copy.copy(self)]
        return rlist

class Expr(Elem): # Exprは一時的なものである
    """
    # Expr
    式を一時的にまとめておく場所です
    ## returns
    get_contents() -> <expr>
    """
    def __init__(self, name: str, contents: list, depth:int) -> None:
        super().__init__(name, contents, depth)

    def resolve_self(self):
        """
        # resolve_self
        """
        expr_parser = Expr_parser(self.contents,depth = self.depth)
        self.contents = expr_parser.resolve()

    def __repr__(self):
        return f"<{type(self).__name__} depth:({self.depth}) expr:({self.contents})>"

    def get_all_local_value(self):
        rlist:list = list()
        for i in self.contents:
            local_value = i.get_all_local_value()
            rlist += local_value
        return rlist

class ControlStatement(Elem):
    """
    # ControlStatement
    ## 制御文
    制御文とは以下のようなものである
    ```
    return <expr> ;
    break  <expr> ;
    continue ;
    assert <expr> ;
    ```
    <expr>はparserの段階ではoptionalである。

    Lichenではif 文やfor loop while から抜ける際に
    breakに式を渡すことで値を返却することができる    

    # returns
    get_name() -> <name> (name| return, break, continue, assert)
    get_contents() -> <expr> 
    """
    def __init__(self, name: str, expr: str, depth:int) -> None:
        super().__init__(name, expr, depth)
    
    def wat_format_gen(self):
        """
        # wat_format_gen
        ## 
        場合によって大きく対応が変わるので注意
        - ループ内にあるばあい
        - else
        - if elif else文にある場合
        - else
        """
        pass

    def resolve_self(self):
        expr_parser = Expr_parser(self.contents, depth = self.depth + 1)
        self.contents = expr_parser.resolve()
    
    def get_all_local_value(self):
        rlist:list = list()
        for i in self.contents:
            local_value = i.get_all_local_value()
            rlist += local_value
        return rlist

# === Parser ===

class Expr_parser(Parser): # 式について解決します
    """
    # expressions resolver
    ## 式について解決します
    """
    def __init__(self, code: str,depth = 0) -> None:
        super().__init__(code)
        self.depth = depth

    def grouping_syntaxbox(self,vec:list) -> list:
        """
        # grouping_syntaxbox
        
        """
        flag:bool = False
        name:str = None
        group:list = list()
        rlist:list = list()
        for i in vec:
            if type(i) is Syntax:
                if i.get_name() in ["if", "loop", "while", "for"]:
                    flag = True
                    name = i.get_name()
                    group.append(i)
                elif i.get_name() == "elif":
                    if flag:
                        group.append(i)
                    else: # flagが上がっていないのにelifが来た場合はerror
                        print("Error!")                         # TODO 
                elif i.get_name() == "else":
                    if flag:
                        group.append(i)
                        rlist.append(SyntaxBox(name,copy.copy(group),self.depth))
                        group.clear()
                        name = None
                        flag = False
                    else: # flagが上がっていないのにelifが来た場合はerror
                        print("Error!")                         # TODO
                else: # 上記以外の制御式
                    rlist.append(i)
            else:
                if flag:
                    if group:
                        rlist.append(SyntaxBox(name,copy.copy(group),self.depth))
                        group.clear()
                        name = None
                    else: # group is empty
                        pass
                    flag = False
                else:
                    pass
                rlist.append(i)
        if group:
            rlist.append(SyntaxBox(name,copy.copy(group),self.depth))
        return rlist

    def code2vec(self,code:str) ->list:
        # クォーテーションをまとめる
        codelist = self.resolve_quotation(code, "\"")
        # ブロック、リストブロック、パレンブロック Elemをまとめる
        for i in self.blocks:codelist = self.grouping_elements(codelist, *i)
        # Wordをまとめる
        codelist = self.grouping_words(codelist, self.split, self.word_excludes)
        ## if, elif, else, forをまとめる
        codelist = self.grouping_syntax(codelist, self.syntax_words)
        ## if, elif, else, forをまとめる2
        codelist =self.grouping_syntaxbox(codelist)
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
    def __init__(self, code: str, depth = 0) -> None:
        super().__init__(code)
        self.depth = depth

    def code2vec(self, code: str) -> list:
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
        #codelist = self.grouping_operator(codelist,self.length_order_ope_list)
        ## 演算子を解決する
        #codelist = self.resolve_operation(codelist)
        # State_parser固有の処理
        ## 関数宣言をまとめる
        codelist = self.grouping_decfunc(codelist)
        ## 変数定数宣言をまとめる
        codelist = self.grouping_decvalue(codelist)
        ## return,continue,breakなどをまとめる
        codelist = self.grouping_controlstatement(codelist)
        ## 変数、関数宣言がpublicかどうかを調べる
        codelist = self.public_checker(codelist) 

        codelist = self.grouping_expr(codelist,self.expr_excludes)
        return codelist

    def grouping_decfunc(self,vec:list["Elem"]) -> list:
        """
        # grouping_decfunc 
        関数宣言部分を切り分けます
        継承先、State_parserで使用するmethod
        """
        # bool
        flag:bool = False
        return_type_flag:bool = False
        # str
        func_name:str = None
        # list
        func_args:list = list()
        rtype_group:list = list()
        rlist:list = list()
        for i in vec:
            if type(i) is Word:
                if i.get_contents() == self.FUNCTION:
                    flag = True
                elif return_type_flag:
                    rtype_group.append(i)
                else:
                    rlist.append(i)
            elif type(i) is Func and flag:
                func_name = i.get_name()
                func_args = i.get_contents()
            elif flag and  type(i) is Block:
                rlist.append(DecFunc( func_name, copy.copy(func_args), copy.copy(rtype_group), i, False, self.depth))
                flag = False
                return_type_flag = False
                rtype_group.clear()
                func_args.clear()
            elif type(i) is str and i == ":" and flag:
                return_type_flag = True
            elif return_type_flag:
                rtype_group.append(i)
            else:
                rlist.append(i)
        return rlist

    def grouping_decvalue(self, vec: list["Elem"]) -> list:
        """
        # grouping_decvalue
        (const|let) <name>:<type> = <expr>;
        - TODO :ハードコーディングを解消
        """
        ## bool
        flag:bool = False
        type_flag:bool = False
        assignment_flag:bool = False
        ## str
        mutable:str = None
        value_name:str = None
        ## list
        rtype_group:list = list()
        contents_group:list = list()
        rlist:list = list()
        for i in vec:
            if type(i) is Word and i.get_contents() in self.value_dec_mutable: # const,let を見つけたら宣言開始
                flag = True
                mutable = i.get_contents()
            elif assignment_flag: # <expr> 追加 contents_group
                # <expr>
                if type(i) is str and i == ';': # 宣言の終了
                    #print(mutable,value_name,rtype_group,contents_group)
                    flag, type_flag, assignment_flag , mutable, value_name = self.__group_contents_decvalue(mutable, value_name, rtype_group, contents_group, rlist)
                else:
                    # ここでのiは代入する<expr>の一部
                    contents_group.append(i)
            elif type_flag: # <expr> 追加 rtype_group
                if type(i) is str:
                    if i == '=':
                        assignment_flag = True
                    elif i == ';':
                        flag, type_flag, assignment_flag, mutable, value_name = self.__group_contents_decvalue(mutable, value_name, rtype_group, contents_group, rlist)
                    else:
                        rtype_group.append(i)
                else:
                    # ここでのiは<type>の一部
                    rtype_group.append(i)
            elif flag: # 
                if type(i) is str:
                    if i == ':': # タイプ宣言の始まり
                        type_flag = True
                    elif i == ';': # 宣言の終了
                        flag,type_flag,assignment_flag, mutable, value_name = self.__group_contents_decvalue(mutable, value_name, rtype_group, contents_group, rlist)
                    elif i == '=': 
                        # 代入とセットになっている宣言の始まり
                        # タイプ宣言がない
                        assignment_flag = True
                    else:
                        rlist.append(i)
                elif type(i) is Word:
                    value_name = i.get_contents()
                else:
                    print("Error!") # 
                    return
            else:
                rlist.append(i)
        return rlist

    def __group_contents_decvalue(self, mutable, value_name, rtype_group, contents_group, rlist):
        """
        # __group_contents_decvalue
        """
        rlist.append(DecValue(mutable,value_name,copy.copy(rtype_group),copy.copy(contents_group),self.depth))
        rtype_group.clear()
        contents_group.clear()
        value_name = None
        mutable = None
        flag = False
        type_flag = False
        assignment_flag = False
        return flag,type_flag,assignment_flag,mutable,value_name

    def grouping_controlstatement(self,vec: list["Elem"]):
        """
        # grouping_controlstatement
        制御文をまとめる
        """
        flag:bool = False
        name:str = None
        expr_group:list = list()
        rlist:list = list()
        for i in vec:
            if type(i) is Word and i.get_contents() in self.control_statement:
                name = i.get_contents() # name :example (return, break ,continue, assert)
                flag = True
            elif type(i) is str and i == ';' and flag:
                rlist.append(ControlStatement(name,copy.copy(expr_group),self.depth))
                expr_group.clear()
                flag = False
            elif flag:
                expr_group.append(i)
            else:
                rlist.append(i)
        return rlist
    
    def public_checker(self,vec:list["Elem"]):
        """
        # public_checker
        pub <decfunc>
        pub <decvalue>
        """
        pub_flag:bool = False
        rlist:list = list()
        for i in vec:
            if type(i) is Word and i.get_contents() == "pub":
                pub_flag = True
            elif pub_flag and (type(i) is DecFunc or type(i) is DecValue):
                i.pub_flag = True
                rlist.append(i)
                pub_flag = False
            else:
                rlist.append(i)
        return rlist

    def grouping_expr(self,vec:list["Elem"],excludes:list) -> list:
        """
        # grouping_expr
        excludes [DecFunc, DecValue, ControlStatement]
        """
        group:list = list()
        rlist:list = list()
        for i in vec:
            if any(map(lambda a:type (i) is a,excludes)):
                if group:
                    rlist.append(Expr(None,copy.copy(group),self.depth))
                    group.clear()
                rlist.append(i)
            elif type(i) is str and i == ";":
                rlist.append(Expr(None,copy.copy(group),self.depth))
                group.clear()
            else:
                group.append(i)
        if group:
            rlist.append(Expr(None,copy.copy(group),self.depth))
        return rlist

    def resolve(self):
        codelist = self.code2vec(self.code)
        for i in codelist:
            i.resolve_self()
        return codelist

# Type_Elem
class Type_Elem(Elem):
    """
    # Type_Elem
    タイプ宣言用
    """
    def __init__(self, name: str, contents: str) -> None:
        super().__init__(name, contents)    

class Type_i32(Type_Elem):
    def __init__(self, name: str, contents: str) -> None:
        super().__init__(name, contents)

class Type_i64(Type_Elem):
    def __init__(self, name: str, contents: str) -> None:
        super().__init__(name, contents)

class Type_f32(Type_Elem):
    def __init__(self, name: str, contents: str) -> None:
        super().__init__(name, contents)

class Type_f64(Type_Elem):
    def __init__(self, name: str, contents: str) -> None:
        super().__init__(name, contents)

class Type_Char(Type_Elem):
    def __init__(self, name: str, contents: str) -> None:
        super().__init__(name, contents)

# typeの解析
class Type_parser(Parser):
    """
    # Type_parser
    型解析用
    """
    def __init__(self,code:str) -> None:
        self.code = code
    
    def code2vec(self, code: str) -> list[str]:
        """
        # code2vec
        type解析用
        """
        return super().code2vec(code)

    def resolve(self):
        pass

