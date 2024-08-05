"""
# Lichen parser cray model
Class parser

TODO : コメントをかけるようにする

"""
import copy
import logging

logging.basicConfig(format="%(lineno)s:%(levelname)s:%(message)s", level=logging.DEBUG)
# logging.disable()

# === Parser ===

class Parser:
    # resolve <expr>
    # 式を解決します
    def __init__(self, code:str,loopdepth = 0,depth = 0) -> None:
        self.code:str = code
        self.loopdepth = loopdepth
        self.depth:int = depth

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
            "%=":-4,
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
        self.syntax_words_heads = [
            "if",
            "loop",
            "for",
            "while",
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
        rlist:list = []
        group:list = []
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
                        # position = (newline_counter,column_counter)
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
        rlist:list[str] = []
        group:list[str] = []
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
                    rlist.append(ObjectInstance(
                        None,
                        copy.copy(group),
                        self.depth,
                        self.loopdepth
                    ))
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
                                self.depth,
                                self.loopdepth
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
                                self.depth,
                                self.loopdepth
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

    def contain_callable(self,vec:list):
        """
        callableな状態があってかつそれが呼ばれようとしているときに、true
        ```
        anyfunc()()
        ^^^^^^^^^
        '-> this is callable!
        
        anyfunc()
        ^^^^^^^^^
        '-> this is not callable

        anylist[]()
        ^^^^^^^^^
        '-> this is callable!
        """
        flag:bool = False
        name_tmp:Word|Func = None
    
        for i in vec:
            if (type(i) is Word) or (type(i) is Func):
                name_tmp  = i
                flag = True
            elif type(i) is ParenBlock:
                if flag and name_tmp.contents not in self.control_statement:
                    return True
            else:
                if flag:
                    flag = False
                    name_tmp = None
                else:
                    pass
        return False

    def grouping_functioncall(self,vec:list) -> list:
        """
        # grouping_call
        ## group function calls
        ```python
        grouping_call(vec,[Word],Parenblock,Func) -> list:
        ```
        TODO:ここでは、returnやbreak,continueが関数として認識されないようにする
        """
        flag:bool = False
        name_tmp:Word | Func = None
        rlist:list = []
        logging.debug(vec)
        for i in vec:
            if (type(i) is Word) or (type(i) is Func):
                if flag:
                    rlist.append(name_tmp)
                name_tmp  = i
                flag = True
            elif type(i) is ParenBlock:
                if flag and name_tmp.contents not in self.control_statement:
                    # return ();みたいなかっこ悪い書き方もできる！
                    # logging.debug(obj)
                    rlist.append(
                        Func(
                            name_tmp,# func name
                            i.get_contents(),       #self.comma_spliter(i.get_contents()), # args(list[<expr>,..])
                            self.depth,
                            self.loopdepth
                        )
                    )
                    name_tmp = None
                    flag = False
                else:
                    if name_tmp is not None:
                        rlist.append(name_tmp)
                    rlist.append(i)
                    name_tmp = None
            else:
                if flag:
                    if name_tmp is not None:
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
        group:list = [] # index格納用
        rlist:list = []
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
                        rlist.append(List(expr,copy.copy(group),self.depth,self.loopdepth))
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
                    rlist.append(List(expr,copy.copy(group),self.depth,self.loopdepth))
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
        # grouping_operator
        ## 2** -1
        """
        rlist:list = copy.copy(vec)
        for i in ordered_opelist:
            rlist = self.grouping_operator_unit(rlist,i)
        return rlist

    def grouping_lambda(self,vec:list) -> list:
        """
        # grouping_lambda 
        この関数は関数内で宣言された関数、
        Lichenではとりあえず関数ないで宣言できる関数を無名関数のみに絞ることで式指向を実現させる
        """
        rlist:list = []
        args_tmp = None
        block_tmp = None
        return_type_tmp = []
        flag1:bool = False
        # flag2:bool = False

        logging.debug(vec)
        for i in vec:
            #　関数から関数が返却されていて直接callされているようなシチュエーションの時を想定している
            # TODO 他にも、リストから返却されてた関数ポインタをコールする場合など色々な場合を考慮する必要がある
            if (type(i) is Func) and (type(i.get_name()) is Word) and (i.get_name().get_contents() == "fn"):
                flag1 = True
                args_tmp = i.get_contents()
            elif type(i) is Block:
                if flag1:
                    block_tmp = i
                    rlist.append(
                        DecLambda(
                            copy.deepcopy(args_tmp),
                            copy.deepcopy(return_type_tmp),
                            block_tmp.get_contents(),
                            self.depth,
                            self.loopdepth
                        )
                    )
                    return_type_tmp.clear()
                    flag1 = False
                else:
                    rlist.append(i)
            elif flag1:
                return_type_tmp.append(i)
            else:
                rlist.append(i)
        return rlist

        # for i in vec:
        #     if type(i) is Word and i.get_contents() == "fn":
        #         flag1 = True
        #     elif flag1:
        #         if type(i) is ParenBlock:
        #             args_tmp = i
        #             flag1 = False
        #             flag2 = True
        #         else:
        #             raise BaseException("invalid syntax error fn token")
        #     elif flag2:
        #         if type(i) is Block:
        #             block_tmp = i
        #             rlist.append(
        #                 DecLambda(
        #                     args_tmp,
        #                     copy.deepcopy(return_type_tmp),
        #                     block_tmp.get_contents(),
        #                     self.depth,
        #                     self.loopdepth
        #                 )
        #             )
        #             return_type_tmp.clear()
        #             flag1,flag2 = False,False
        #         else:
        #             # ここでreturn タイプを採取する
        #             return_type_tmp.append(i)
        #     else:
        #         rlist.append(i)
        # if flag1 or flag2:
        #     raise BaseException("invalid syntax error fn token")
        # return rlist

    # comma_spliter
    def comma_spliter(self,vec:list) -> list:
        """
        # comma_spliter 
        (a,b,c,) == (a,b,c)
        [a,b,c,] == (a,b,c)
        ## 各要素を式として処理する
        """
        group:list = []
        rlist:list = []
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
        for i in self.blocks:
            codelist = self.grouping_elements(codelist, *i)
        # Wordをまとめる
        codelist = self.grouping_words(codelist, self.split, self.word_excludes)
        ## if, elif, else, forをまとめる
        codelist = self.grouping_syntax(codelist, self.syntax_words)
        ## functionの呼び出しをまとめる
        while self.contain_callable(codelist):
            codelist = self.grouping_functioncall(codelist)
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
                self.depth,
                self.loopdepth
            )]
        else:
            return vec

    def resolve(self) -> list["Elem"]:
        return self.code2vec(self.code)

    def __resolve_func_arg_unit(self,code:list):
        codelist = self.grouping_words(code, self.split, self.word_excludes)
        return codelist

    def resolve_func_arg(self) -> list:
        """
        # resolve_func_arg
        関数の引数の解決
        """
        rlist:list = list()
        rlist = self.__resolve_func_arg_unit(self.code)
        rlist = self.comma_spliter(rlist)
        return rlist


class Expr_parser(Parser): # 式について解決します
    """
    # expressions resolver
    ## 式について解決します
    """
    def __init__(self, code: str, loopdepth = 0,depth = 0) -> None:
        super().__init__(code,loopdepth=loopdepth)
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
                if i.get_name() in self.syntax_words_heads:
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
                        rlist.append(SyntaxBox(name,copy.copy(group),self.depth,self.loopdepth))
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
                        rlist.append(SyntaxBox(name,copy.copy(group),self.depth,self.loopdepth))
                        group.clear()
                        name = None
                    else: # group is empty
                        pass
                    flag = False
                else:
                    pass
                rlist.append(i)
        if group:
            rlist.append(SyntaxBox(name,copy.copy(group),self.depth,self.loopdepth))
        return rlist

    def code2vec(self,code:str) ->list:
        # クォーテーションをまとめる
        codelist = self.resolve_quotation(code, "\"")
        # ブロック、リストブロック、パレンブロック Elemをまとめる
        for i in self.blocks:
            codelist = self.grouping_elements(codelist, *i)
        # Wordをまとめる
        codelist = self.grouping_words(codelist, self.split, self.word_excludes)
        ## if, elif, else, forをまとめる
        codelist = self.grouping_syntax(codelist, self.syntax_words)
        ## if, elif, else, forをまとめる2
        codelist = self.grouping_syntaxbox(codelist)
        codelist = self.grouping_lambda(codelist)
        ## functionの呼び出しをまとめる
        while self.contain_callable(codelist):
            codelist = self.grouping_functioncall(codelist)
        ## listの呼び出しをまとめる
        codelist = self.grouping_list(codelist,[Word,Func,ListBlock,Syntax],ListBlock,List)
        ## 演算子をまとめる
        codelist = self.grouping_operator(codelist,self.length_order_ope_list)
        ## 演算子を解決する
        codelist = self.resolve_operation(codelist)
        return codelist

    def resolve(self) -> list["Elem"]:
        codelist = self.code2vec(self.code)
        logging.debug(codelist)
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
    def __init__(self, code: str, loopdepth = 0, depth = 0) -> None:
        super().__init__(code,loopdepth=loopdepth)
        self.depth = depth

    def code2vec(self, code: str) -> list:
        # クォーテーションをまとめる
        codelist = self.resolve_quotation(code, "\"")
        # ブロック、リストブロック、パレンブロック Elemをまとめる
        for i in self.blocks:
            codelist = self.grouping_elements(codelist, *i)
        # Wordをまとめる
        codelist = self.grouping_words(codelist, self.split, self.word_excludes)
        ## if, elif, else, forをまとめる
        codelist = self.grouping_syntax(codelist, self.syntax_words)
        ## functionの呼び出しをまとめる

        while self.contain_callable(codelist):
            codelist = self.grouping_functioncall(codelist)
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
        func_args:list = []
        rtype_group:list = []
        rlist:list = []
        for i in vec:
            if type(i) is Word:
                if return_type_flag:
                    rtype_group.append(i)
                elif i.get_contents() == self.FUNCTION:
                    flag = True
                else:
                    rlist.append(i)
            elif type(i) is Func:
                if return_type_flag:
                    rtype_group.append(i)
                elif flag:
                    func_name = i.get_name()
                    func_args = i.get_contents()
                else:
                    rlist.append(i)
            elif flag and  type(i) is Block:
                logging.debug(f"function name {rtype_group}")
                rlist.append(DecFunc( 
                    copy.deepcopy(func_name),              # funcname 
                    copy.deepcopy(func_args),   # args
                    copy.deepcopy(rtype_group), # rtype
                    i,                      # contents
                    False,                  #
                    self.depth              # 
                ))
                flag = False
                return_type_flag = False
                rtype_group.clear()
                func_args.clear()
            elif isinstance(i, str) and i == ":" and flag:
                return_type_flag = True
                # rtype_group.append(i)
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
                if isinstance(i,str) and i == ';': # 宣言の終了
                    #print(mutable,value_name,rtype_group,contents_group)
                    flag, type_flag, assignment_flag , mutable, value_name = self.__group_contents_decvalue(mutable, value_name, rtype_group, contents_group, rlist)
                else:
                    # ここでのiは代入する<expr>の一部
                    contents_group.append(i)
            elif type_flag: # <expr> 追加 rtype_group
                if isinstance(i,str):
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
                if isinstance(i,str):
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
        rlist.append(DecValue(mutable,value_name,copy.copy(rtype_group),copy.copy(contents_group),self.depth,self.loopdepth))
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
            #print(i)
            if type(i) is Word and i.get_contents() in self.control_statement:
                name = i.get_contents() # name :example (return, break ,continue, assert)
                flag = True
            elif isinstance(i, str) and i == ';' and flag:
                rlist.append(ControlStatement(name,copy.copy(expr_group),self.depth,self.loopdepth))
                expr_group.clear()
                flag = False
            elif flag:
                expr_group.append(i)
            else:
                rlist.append(i)
        #print("+"*30)
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
                    rlist.append(Expr(None,copy.copy(group),self.depth,self.loopdepth))
                    group.clear()
                rlist.append(i)
            elif isinstance(i, str) and i == ";":
                rlist.append(Expr(None,copy.copy(group),self.depth,self.loopdepth))
                group.clear()
            else:
                group.append(i)
        if group:
            rlist.append(Expr(None,copy.copy(group),self.depth,self.loopdepth))
        return rlist

    def resolve(self) -> list["Elem"]:
        codelist = self.code2vec(self.code)
        #print(codelist)
        for i in codelist:
            i.resolve_self()
        return codelist

    def toplevel_resolve(self):
        """
        # toplevel_resolve 
        入力されたコードに対して、本番環境でほしい成果物を出力する
        ## 主な処理
        - import したい関数の呼び出し
        - exportしたい関数pub関数
        """
        wasm_code:str = ""
        wasm_code += "(module\n"
        codelist = self.resolve()
        export_functions:list = []
        for elem in codelist:
            if type(elem) is DecFunc:
                if elem.pub_flag:
                    export_functions.append(elem.get_name())
                wasm_code += elem.wat_format_gen()
            else:
                # function 以外の要素がトップレベルに配置された場合
                raise BaseException("Only functions can be placed at the top level")
        # ここで、exportしたい関数をまとめて宣言する
        # (export "gcd" (func $gcd))
        for funcname in export_functions:
            wasm_code += "(export \"{}\" (func ${}))\n".format(funcname,funcname)
        wasm_code += ")"

        return wasm_code


class Args_parser(Parser):

    def __init__(self, code: str, loopdepth=0, depth=0) -> None:
        super().__init__(code, loopdepth, depth)
        self.blocks = [
            ('(',')',ParenBlock),
            ('<','>',TypeBlock)
        ]


    def code2vec(self,code:list):
        for i in self.blocks:
            codelist = self.grouping_elements(code, *i)
        codelist = self.grouping_words(codelist, self.split, self.word_excludes)
        return codelist

    def resolve_func_arg(self) -> list:
        """
        # resolve_func_arg
        関数の引数の解決
        """
        rlist:list = []
        rlist = self.code2vec(self.code)
        #print("codelist",rlist)
        rlist = self.comma_spliter(rlist)
        return rlist


# typeの解析
class Type_parser(Parser):
    """
    # Type_parser
    型解析用
    """
    def __init__(self,code:str,mode = "return") -> None:
        """
        @param mode {str} return or normal

        ## mode

        ### return mode
        return mode のときは、返り値すなわち左に`:`がある状態のtype文字列が渡される

        ### normal mode(default)
        normal mode のときは、<T>におけるTのような一般的な引数の内部についてparseするときに使うmode 
        ## note
        - lichenが基本で用意する型
          - i32,i64,f32,f64 //プリミティブ型
          - () // tupleタプル(格納可能な要素は限定される)
            プリミティブ型だけしか入れられない
          - Vec<T> //実体はタプル
          - Mat<T> //実体はタプル
          - List<T> //実体は先頭ポインター
          - 関数 fn (T,...):T
         
        - 複数値の返却とともに複数値の同時代入も作成する
          ```lc
          let x,y : (i32,i32) = pair(); // pair():(i32,i32)
          ```
          的な文法
         
        - ベクトル、行列の演算
          - Vec2 // 実体は(i32,i32)のタプル
          - Vec3 // 実体は(i32,i32,i32)
          - Vec4
          - Vec5<i32>
          - ...
          - Mat2x2 // 実体は(T, T, T, T)
          - Mat3x4 // 実体は(T, T, T, T, T, T, T, T, T, T, T, T)
          - Mat4x...
          a*b
        """
        # super().__init__(code)
        self.code = code
        self.primitive_types = [
            "i32",
            "i64",
            "f32",
            "f64",
        ]
        self.basic_types = [
            "i32",
            "i64",
            "f32",
            "f64"
        ]
        self.blocks = [
            ['<','>',TypeBlock],
            ['(',')',TypeTuple],
        ]

    def grouping_functype(self,vec:list) -> list:
        """
        # grouping_functype 
        関数ポインタのタイプに関するparseする
        基本的な文法は以下のよう
        ```
        : fn (T,...) : T
        ```
        """
        # rlist:list = []
        for i in vec:
            pass

    def grouping_tupletype(self) -> list:
        """
        # grouping_tupletype
        """
        pass

    def code2vec(self, code: str) -> list[str]:
        """
        # code2vec
        type解析用
        """
        codelist = copy.deepcopy(code)
        codelist = self.grouping_words(codelist, self.split, ['<','>','(',')'])
        for i in self.blocks:
            # コードブロックをかき集める
            codelist = self.grouping_elements(codelist,*i)
        
        return codelist

    def resolve(self) -> list["Elem"]:
        codelist = self.code2vec(self.code)
        for i in codelist:
            i.resolve_self()
        return codelist


# Base Elem
class Elem:
    """
    字句解析用データ型
    """
    def __init__(self, name:str, contents:str,depth:int,loopdepth:int) -> None:
        self.name = name
        self.contents = contents
        self.depth = depth
        self.loopdepth = loopdepth

    def get_contents(self):
        return self.contents

    def get_name(self): 
        return self.name

    def wat_format_gen(self) -> str:
        """
        # wat_format_gen

        """
        return f"({type(self).__name__} 未実装)\n"

    def resolve_self(self):
        """
        # resolve_self
        それぞれのデータ型で再帰的に処理をする
        """
        print(f"resolve_self 未実装 {type(self).__name__}")

    def __repr__(self):
        return f"\n{'    ' * self.depth}<{type(self).__name__} depth:({self.depth}) name:({self.name}) contents:({self.contents})>"

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

        関数内に存在するローカル変数宣言をすべて取得する
        持たない場合は空リストを返却する
        """
        # print(f"{type(self).__name__} get_all_local_value 未実装")
        return []

    def negative_inversion(self):
        """
        外側にかけられた否定を
        ド・モルガンの法則や否定対応テーブル、not同士の相殺を用いて解消する
        Func
        """
        pass

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
    def __init__(self, name: str, contents: list, depth: int, loopdepth: int) -> None:super().__init__(name, contents, depth, loopdepth)

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

    def wat_format_gen(self) -> str:
        """
        # wat_format_gen 
        各々の要素に対してwatcodeを生成させる
        """
        wasm_code:str = str()
        for i in self.contents:
            wasm_code += i.wat_format_gen()
        return wasm_code
        # return "<処理>"

class String(Elem):
    """
    文字列を格納
    "<string>"
    '<char>'
    # returns
    get_contents -> <string> or <char>
    """
    def __init__(self, name: str, contents: str, depth: int) -> None:
        # これ以上深くなることがないのでloopdepthは必要ない
        super().__init__(name, contents, depth,None)

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

    def __init__(self, name: str, contents: list, depth: int, loopdepth: int) -> None:
        super().__init__(name, contents, depth, loopdepth)

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
    def __init__(self, name: str, contents: list, depth: int, loopdepth: int) -> None:
        super().__init__(name, contents, depth, loopdepth)

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

    def negative_inversion(self):
        """
        外側にかけられた否定を
        """
        for i in self.contents:
            i.negative_inversion()

class Word(Elem):# Word Elemは仮どめ
    """
    引数、変数、関数定義、制御文法の文字列
    <word> = fn, let, const, if, while...(exclude: +, -, *, /)
    <word> = <syntax>, <name>, <type>, <Number>
    # returns
    get_contents -> <word>
    """
    def __init__(self, name: str, contents: str, depth: int) -> None:
        """
        # Word
        - 変数の場合
        - 数字の場合
        - boolの場合
        """
        super().__init__(name, contents, depth, None)
        self.bool_flag:bool = True

    def negative_inversion(self):
        self.bool_flag = False
        # return super().negative_inversion()

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
    
    def wat_format_gen(self,minus=False):
        """
        # wat_format_gen
        ## param
        # ある数字が負の値であるとき、 
        ## TODO:数字ではない場合
        """
        if self.__self_is_i32():
            return "i32.const {}{}\n".format(
                '-' if minus else '',
                self.contents
            )
        else:
            return "local.get ${}\n".format(self.contents)
    def __repr__(self):
        return f"\n{'    ' * self.depth}<{type(self).__name__} depth:({self.depth}) name:({self.name}) bool_flag:({self.bool_flag}) contents:({self.contents})>"

class Syntax(Elem):
    """
    # returns
    <syntax> = if, elif, else, loop, for, while
    get_name ->  if, elif, else, loop, for, while
    get_expr -> <expr>
    get_contents -> {<proc>}
    """ 
    def __init__(self, name: str, expr, contents, depth: int, loopdepth: int) -> None:
        super().__init__(name, contents, depth, loopdepth)
        self.expr = expr

    def get_expr(self):
        return self.expr

    def resolve_self(self,isloop = False):
        """
        # resolve_self
        ## if while for loop などを解決する
        """
        loopdepth: int = self.loopdepth + 1 if isloop else self.loopdepth
        state_parser = State_parser(self.contents, depth = self.depth + 1, loopdepth = loopdepth)
        self.contents = state_parser.resolve()
        if self.expr is not None:
            expr_parser = Expr_parser(self.expr, depth = self.depth + 1, loopdepth = loopdepth)
            self.expr = expr_parser.resolve()
        else:
            pass

    def __repr__(self):
        # override
        return f"\n{'    ' * self.depth}<{type(self).__name__} depth:({self.depth}) name:({self.name}) expr:({self.expr}) contents:({self.contents})>"

    def get_all_local_value(self):
        rlist:list = list()
        for i in self.contents:
            local_value = i.get_all_local_value()
            rlist += local_value
        return rlist

    def __proc_if(self,return_type = "None") -> str: # 工事中:TODO
        """
        # __proc_if 
        headがifだった時の処理
        return_type "None"|"return"|""|
        """
        wasm_code:str = ""
        if self.name == "if":
            if self.expr: # <式>
                wasm_code += self.expr[0].wat_format_gen()
            else:
                # ifに条件式が与えられていない場合
                raise BaseException("Error! if節の条件を書いてください")
            if return_type == "None": #                         TODO : 型推論の実装をしたときに変更する
                wasm_code += "if\n"
            else:
                wasm_code += "if (result i32)\n"
            if self.contents: # ブロック内の処理
                wasm_code += self.contents[0].wat_format_gen()
            else:
                raise BaseException("Error!")
        elif self.name == "elif":
            """
            # elif
            ```wat
            else
            ;; <式>
            if
            ;; <処理>
            ```
            """
            wasm_code += "else\n"
            if self.expr:# <式>
                wasm_code += self.expr[0].wat_format_gen()
            else: # ifに条件式が与えられていない場合
                raise BaseException("Error!")
            if return_type == "None": #                         TODO : 型推論の実装をしたときに変更する
                wasm_code += "if\n"
            else:
                wasm_code += "if (result i32)\n"
            if self.contents: # ブロック内の処理
                wasm_code += self.contents[0].wat_format_gen()
            else:
                raise BaseException("Error!")
        elif self.name == "else":
            if self.expr:
                # ここには式は存在しないはず
                raise BaseException("Error!")
            wasm_code += "else\n"
            if self.contents: # ブロック内の処理
                wasm_code += self.contents[0].wat_format_gen()
        else:
            raise BaseException("Error!")
        return wasm_code

    def __proc_loop(self) -> str: # 工事中:TODO
        wasm_code = ""
        if self.name == "loop":
            pass#TODO
        elif self.name == "else":
            pass#TODO
        else:
            raise BaseException("Error!")
        wasm_code += "未実装\n"
        return wasm_code

    def __proc_while(self) -> str: # 工事中:TODO
        """
        ```wasm
        (loop ;; 0
            (block ;;1
                ;;while (i < 10)
                local.get $i
                i32.const 10
                i32.lt_u
                if
                nop
                else
                br 1 ;;end of loop
                end
                ;; ここに処理を書く
                local.get $i
                call $log
                ;; i += 1
                local.get $i
                i32.const 1
                i32.add
                local.set $i
                br 0
            )
        )
        ```
        """
        wasm_code = ""
        if self.name == "while":
            wasm_code += "(loop $#loop{}\n"  .format(self.loopdepth)
            wasm_code += "(block $#block{}\n".format(self.loopdepth)
            if self.get_expr():
                wasm_code += self.expr[0].wat_format_gen()
                # i32.const 1
                # i32.xor
                # br_if block
                #---
                # wasm_code += "if\n"
                # wasm_code += "nop\n"
                # wasm_code += "else\n"
                # wasm_code += "br $#block{} \n".format(self.loopdepth) # TODO
                # wasm_code += "end\n"
                wasm_code += "i32.const 1\n"
                wasm_code += "i32.xor\n"
                wasm_code += "br_if $#block{}\n".format(self.loopdepth)
            else:
                raise BaseException("Error! while節を書いてください")
            # 処理
            for i in self.contents:
                wasm_code += i.wat_format_gen()
            wasm_code += "br $#loop{} \n".format(self.loopdepth) # TODO
            wasm_code += ")"
            wasm_code += ")"
        elif self.name == "else":
            pass#TODO
        else:
            raise BaseException("Error!")
        return wasm_code

    def __proc_for(self) -> str: # 工事中:TODO
        wasm_code = ""
        if self.name == "for":
            pass#TODO
        elif self.name == "else":
            pass#TODO
        else:
            raise BaseException("Error!")
        return wasm_code

    def wat_format_gen(self,syntax_head:str,return_type = "None") -> str:
        """
        # wat_format_gen 
        TODO:これは、非効率的な実装、あとで書き直す
        ## pattern
        - if 
          - if
          - elif
          - else
        - loop
          - loop
          - else
        - while
          - while
          - else
        - for
          - for
          - else
        """
        wasm_code:str = ""
        if syntax_head == "if":
            # wasmとlichenのロジックに従って適切な変換を行う
            wasm_code += self.__proc_if(return_type=return_type)
        elif syntax_head == "loop":
            wasm_code += self.__proc_loop()
        elif syntax_head == "while":
            wasm_code += self.__proc_while()
        elif syntax_head == "for":
            wasm_code += self.__proc_for()
        else:
            raise BaseException("Error!")
        return wasm_code

class SyntaxBox(Elem):
    """
    # SyntaxBox
    if elif else,loop else,while elseなどの連続して解釈されるコードを集めます
    
    """
    def __init__(self, name: str, contents: list[Syntax], depth:int ,loopdepth: int) -> None:
        super().__init__(name, contents, depth, loopdepth)

    def resolve_self(self):
        """
        listの各要素は、すべてSyntaxになっているはずなので、
        それぞれのsyntax要素のresolve_self methodを呼び出せば良い
        ここではparserを呼び出さないのでdepthを深くしない
        """
        for i in self.contents:
            if self.name in ["while","for","loop"]:
                i.resolve_self(isloop = True)
            else:
                i.resolve_self()

    def get_all_local_value(self):
        rlist:list = list()
        for i in self.contents:
            local_value = i.get_all_local_value()
            rlist += local_value
        return rlist

    def __count_name(self,name:str) -> int:
        """
        # __count 
        contentsボックス内の特定のsyntaxを数えます
        """
        counter:int = 0
        for i in self.contents:
            if i.name == name:
                counter += 1
        return counter

    def __include_return_in_contents(self, elements:list) -> bool:
        """
        # __include_return
        """
        for i in elements:
            if type(i) is ControlStatement and i.get_name() == "return":
                return True
        return False

    def __if_has_else(self, elements:list) -> bool:
        return any(
            map(
                lambda a:a.name == "else",
                elements
                )
            )

    def __if_unreachable_checker(self) -> bool:
        """
        # __if_unreachable_checker
        ifに到達する可能性があるのかないのかをcheckするメソッド
        if ステートメントないのすべてのブロックがreturn を含んでいるかどうかをcheckする
        """
        # for i in self.contents:
        #     print(":::",i.contents)
        #     print(self.__include_return_in_contents(i.contents))
        return all(
            map(
                lambda i:
                    self.__include_return_in_contents(i.contents),
                self.contents
                )
            )

    def wat_format_gen(self) -> str:
        """
        # wat_format_gen 
        制御文や、制御式をwasmにして返す
        - if
        - loop
        - for
        - while
        # TODO:if文の実装
        """
        wasm_code = ""
        if self.name == "if":
            # ifが続く場合
            # if 返り値用変数
            # 
            all_if_block_has_return = self.__if_unreachable_checker() and self.__if_has_else(self.contents)
            for i in self.contents:                 # contents内の要素はすべて、syntax
                if all_if_block_has_return:
                    logging.debug(i)
                    wasm_code += i.wat_format_gen("if",return_type = "None") # if elif else
                else:
                    wasm_code += i.wat_format_gen("if",return_type = "i32")
            wasm_code += "end\n"*self.__count_name("elif")            # elif end 開いたelif分だけendで閉じる必要がある
            wasm_code += "end\n"                                      # if ... end このendはifをセットである
            if all_if_block_has_return:
                # すべてのブロックがreturnをした場合end後には到達不可能ため
                wasm_code += "unreachable\n"
        elif self.name == "loop":
            pass # TODO
        elif self.name == "while":
            for i in self.contents:
                wasm_code += i.wat_format_gen("while")
        elif self.name == "for":
            pass # TODO
        else:
            raise BaseException("Error!")
        return wasm_code

class Func(Elem):
    """
    # TODO:resolve args
    srgs:[<expr>,...]のような形を期待する
    <name(excludes: 0-9)>(<expr>,...)
    # returns
    get_contents -> (args:[<expr>,...])
    get_name -> (funcname: <name>)
    """
    def __init__(self, name: "Elem", contents: list, depth:int,loopdepth: int) -> None:
        super().__init__(name, contents, depth, loopdepth)
        # TODO : 引数の型チェックを入れる
        atom_type = "i32"
        self.wasm_ope_correspondence_table:dict = {
            # https://developer.mozilla.org/en-US/docs/WebAssembly/Reference/Numeric
            "+":f"{atom_type}.add", # add
            "-":f"{atom_type}.sub", # sub 
            "*":f"{atom_type}.mul", # mul
            "/":f"{atom_type}.div_u",# div
            "%":f"{atom_type}.rem_u", # mod 

            "==":f"{atom_type}.eq",# Equal => TODO : i32.eqz
            "!=":f"{atom_type}.ne",# Not equal 
            # lt_u lt_sはsigned unsignedの違い気をつける
            "<":f"{atom_type}.lt_s",# Less than
            ">":f"{atom_type}.gt_s", # greater than
            "<=":f"{atom_type}.le_s", # Less or equal
            ">=":f"{atom_type}.ge_s", # greater or equal

            "&&":f"{atom_type}.and", # and
            "||":f"{atom_type}.or", # or

            "=":"local.set"
        }
        self.wasm_special_ope_correspondence_table:dict = {
            "+=":f"{atom_type}.add",
            "-=":f"{atom_type}.sub",
            "*=":f"{atom_type}.mul",
            "/=":f"{atom_type}.div_u",
            "%=":f"{atom_type}.rem_u",
        }
        # not !
        self.not_ope:str = "!"
        self.wasm_not:str = f"""{atom_type}.const 1
{atom_type}.xor
"""
        # 否定の対応表
        self.negative_correspondence_table:dict = {
            ">=":"<",
            "<=":">",
            ">":"<=",
            "<":">=",
        }
        self.nop = "#" # 何もしない関数の名前

    def wat_format_gen(self) -> str:
        """
        # Func.wat_format_gen
        
        ## TODO:否定!などのprefixについての処理

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
            elif self.name.get_contents() in self.wasm_special_ope_correspondence_table:
                # `+=`や`-=`のとき
                # 演算子は両脇に2つの引数を取る
                wasm_code += "local.get ${}\n".format(self.contents[0][0].contents)
                #print("-"*50,self.wasm_special_ope_correspondence_table[self.name.get_contents()],self.contents[0][0],self.contents[1][0])
                wasm_code += self.contents[1][0].wat_format_gen()
                wasm_code += self.wasm_special_ope_correspondence_table[self.name.get_contents()] + "\n"
                wasm_code += "local.set ${}\n".format(self.contents[0][0].contents)
            elif self.name.get_contents() in self.wasm_ope_correspondence_table:
                # 普通の演算子(代入やincrではない)場合
                #
                # 特別な演算子、incr decrの場合は別の処理をする
                if len(self.contents) == 2:
                    call_name = self.wasm_ope_correspondence_table[self.name.get_contents()]
                    if self.contents[0]:
                        # 通常と同じ
                        wasm_code += self.contents[0][0].wat_format_gen() # 左側
                        wasm_code += self.contents[1][0].wat_format_gen() # 右側
                        wasm_code += call_name + '\n'
                    else: # self.contents[0]が空の配列だった場合
                        # -10のような書き方をしている場合
                        # 以下のように変換したい
                        # const.i32 -10
                        if self.name.get_contents() == "+":
                            wasm_code += self.contents[1][0].wat_format_gen(minus = False)
                        elif self.name.get_contents() == "-":
                            # 例.
                            # const.i32 -10
                            # self.contents[1][0] # これは絶対にWordオブジェクトになる
                            wasm_code += self.contents[1][0].wat_format_gen(minus = True)
                        else: # 例えば"/10"みたいな書き方がエラー
                            raise BaseException("Error!:invalid syntax")
                else:
                    # 二項演算の引数が2つ以上またはそれ以下
                    raise BaseException("Error!")
                # call_name = self.wasm_ope_correspondence_table[self.name.get_contents()]
                # print(self.contents)
                # for i in self.contents: # per arg
                #     if len(i) == 0:        # TODO
                #         pass
                #     else:
                #         wasm_code += i[0].wat_format_gen()
                # wasm_code += call_name + '\n'
            elif self.name.get_contents() == self.not_ope:
                # not のときの特別な処理
                #print("not ope",self.contents[1][0])
                wasm_code += self.contents[1][0].wat_format_gen()
                wasm_code += self.wasm_not
            else:
                call_name = self.wasm_ope_correspondence_table[self.name.get_contents()]
                #print(self.contents)
                for i in self.contents: # per arg
                    if len(i) == 0:        # TODO
                        pass
                    else:
                        wasm_code += i[0].wat_format_gen()
                wasm_code += call_name + '\n'
        elif isinstance(self.name, str):
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
        # args = self.get_contents()
        # self.contents = [self.resolve_self_unit(i) for i in args]
        if type(self.get_name()) is Operator:
            args = self.get_contents()
            self.contents = [self.resolve_self_unit(i) for i in args]
        else:
            expr_parser = Parser(self.contents, depth = self.depth + 1)
            self.contents = expr_parser.resolve()
            self.contents = [Expr_parser(i,depth=self.depth+1).resolve() for i in self.contents]

    def negative_inversion(self): # TODO 後で実装
        """
        `!func() === Func<func()>.negative_inversion()`
        外側にかけられた否定を
        - ド・モルガンの法則
        - 否定対応テーブル
        - not同士の相殺
        を用いて解消する
        """
        if type(self.name) is Operator:
            if self.name.ope in self.negative_correspondence_table.keys():
                self.name = Operator(self.negative_correspondence_table[self.name.ope], self.depth)
            elif self.name.ope == "&&":
                # ド・モルガン
                self.name = "||"
                for i in self.contents:
                    if len(i) > 0:
                        i[0].negative_inversion()
            elif self.name.ope == "||":
                # ド・モルガン
                self.name = "&&"
                for i in self.contents:
                    if len(i) > 0:
                        i[0].negative_inversion()
            elif self.name.ope == "!":
                self.name = self.nop
                for i in self.contents:
                    if len(i) > 0:
                        i[0].negative_inversion()
            else:
                # 普通の関数の場合は特に何もしない
                pass
        else:
            pass

    def __repr__(self) -> str:
        return f"\n{'     '*self.depth}<{type(self).__name__} func name:({self.name}) args:({self.contents})>"

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
    def __init__(self, expr: str, index: list[ListBlock],depth:int, loopdepth: int) -> None:
        super().__init__(None, None, depth, loopdepth)
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
        return f"\n{'    ' * self.depth}<{type(self).__name__} depth:({self.depth}) expr:({self.expr}) index:({self.index_list})>"

class Operator(Elem):
    """
    # returns
    get_contents -> ope(ope:["+","-","*","/",...])
    """

    def __init__(self, ope:str, depth:int) -> None:
        super().__init__(None, ope, depth, None)
        self.ope = ope

    def __repr__(self):
        return f"\n{'    ' * self.depth}<{type(self).__name__} depth:({self.depth}) ope:({self.ope})>"

class Data(Elem):
    """
    # Data
    カンマ区切りのデータに対して処理を行います。
    """
    def __init__(self,data:list, depth:int) -> None:
        super().__init__(None, None, depth, None)
        self.data:list = data

    def get_data(self):
        return self.data

    def __repr__(self):
        text:str = ""
        for i in self.data:
            text += repr(i) + ",\n"
        return f"\n{'    ' * self.depth}<{type(self).__name__} depth:({self.depth}) data:({text})>"

class Arg(Elem):
    """
    # ArgParse
    ## 引数エレメント
    """
    def __init__(self, name: str, type_: str, depth:int) -> None:
        super().__init__(name, type_, depth ,None)

class Arg2(Elem):
    """
    # ArgParse
    ## 引数とその型のデータを保持する
    
    args dash [
        <Arg2 depth:(0) name:(a) contents:(['Vec', ['i', '3', '2']])>,
        <Arg2 depth:(0) name:(b) contents:(['Vec', ['i', '3', '2']])>,
        <Arg2 depth:(0) name:(c) contents:(['i32'])>,
        <Arg2 depth:(0) name:(d) contents:(['fn(i32)', 'i32'])>,
        <Arg2 depth:(0) name:(e) contents:(['fn(Vec', ['i', '3', '2'], ')', 'i32'])>
    ]
    """
    def __init__(self, name: str, contents: list, depth: int) -> None:
        super().__init__(name, contents, depth, None)
    
    def grouping_words():
        pass
    def resolve_self(self):
        """
        型を解釈する
        ここでは、タイプ型と、引数変数型の区別がついている必要がある
        """
        pass


### function declaration
class DecFunc(Elem):
    """
    関数の宣言部分
    (pub) fn <name><parenblock>:<type> <block>
    args
    TODO:decfunc内で使用するローカル変数をすべて取得するメソッドを作成する
    """
    def __init__(self, funcname:str,args:list,return_type, contents: Block,pub_flag:bool, depth:int) -> None:
        super().__init__(funcname, contents, depth, 0)
        self.return_type = return_type # 返り値のタイプ
        self.args = args
        self.pub_flag  = pub_flag

    def arg_parse(self,args_list:list[list]) -> list[Arg]:
        """
        # arg_parse
        arg_list : [[<word>,":",<word>],[<word>,":",<word>]]
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
            rlist.append(Arg(name, type_, self.depth))
        return rlist

    def arg_parse2(self,args_list:list[list]) -> list[Arg2]:
        """
        # arg_parse
        arg_list : [[<word>,":",<type>],[<word>,":",<type>]]
        このような形のリスト
        """
        rlist:list = list()
        for i in args_list:
            flag:bool = False
            name = None
            type_ = []
            for j in i:
                if isinstance(j, str):
                    if j == ":":
                        flag = True
                    else:
                        if flag:
                            type_.append(j)
                        else:
                            raise BaseException("引数部分が不正な文法です")
                else:
                    if flag:
                        # type
                        type_.append(j.get_contents())
                    else:
                        # name
                        name = j.get_contents()
            rlist.append(Arg2(name, type_, self.depth))
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
        for i in args:                                                       # TODO: 自作の型などについての設定
            wasm_code += "(param ${} {})\n".format(i.get_name(),i.get_contents())
        if r_type:                                                           # TODO: 自作の型などについての設定
            # 型の処理
            if r_type[0].get_contents() == "void":
                pass
            else:  #TODO: 仮
                if isinstance(r_type[0].get_contents(),list):
                    wasm_code += "(result {})\n".format(" ".join(r_type[0].get_contents()))
                else:
                    wasm_code += "(result {})\n".format(r_type[0].get_contents())
        else:
            raise BaseException("返り値が設定されていません")
        for i in self.get_all_local_value():
            type_ = i.get_type()
            # TODO: default is i32 あとで型の推論をできるように実装
            # TODO: 様々な型に対応させる
            # print("local","$"+i.get_name(),type_[0].contents if type_ else "i32")
            wasm_code += ' '.join(["(local","$"+i.get_name(),(type_[0].contents if type_ else "i32") + ")\n"])
        # TODO : ここに処理を書く
        if self.contents:
            # self.contentsはBlock
            wasm_code += self.contents.wat_format_gen()
        else:
            raise BaseException("Error!")
        wasm_code += ")\n" # close func
        return wasm_code

    def resolve_self(self):
        """
        # resolve_self
        # TODO argsのtypeの処理
        """
        #print("args", self.args)
        # logging.debug("=====logger=======> %s" % str(self.return_type))
        parser = Args_parser(self.args, depth = self.depth + 1)
        self.args = parser.resolve_func_arg()
        #print("args", self.args)
        #print("args dash",self.arg_parse2(self.args))
        # ここでタイプを変更する関数を作成する
        self.contents.resolve_self()

    def __repr__(self): # public 関数のときの表示
        return f"\n{'    ' * self.depth}<{type(self).__name__} depth:({self.depth}) pubflag({self.pub_flag}) funcname:({self.name}) args:({self.args}) return type:({self.return_type}) contents:({self.contents})>"

    def get_all_local_value(self) -> list:
        """
        # get_all_local_value
        decfunc内で使用するローカル変数をすべて取得するメソッドを作成する
        decvalueのリスト
        """
        # rlist:list = list()
        # error check
        if type(self.contents) is Block:
            #print ("decfunc".center(50,'='))
            pass
        else:
            print ("Error! : function contetns is not Block")
        return self.contents.get_all_local_value()

class DecLambda(Elem):
    def __init__(self,args,return_type, contents: str, depth: int, loopdepth: int) -> None:
        super().__init__(
            None,
            contents,
            depth,
            loopdepth
        )
        self.return_type = return_type
        self.args = args

    def resolve_self(self):
        # TODO: resolve args :self.args
        # TODO: resolve args :self.return_type
        state_parser = State_parser(self.contents,loopdepth = self.loopdepth,depth = self.depth + 1)
        self.contents = state_parser.resolve()

    def __repr__(self):
        return f"\n{'    ' * self.depth}<{type(self).__name__} depth:({self.depth}) args:({self.args}) rtype:({self.return_type}) contents:({self.contents})>"
    

class DecValue(Elem):
    """
    変数の宣言
    (pub) (const|let) <name>:<type> = <expr>;
    ## returns
    get_name() -> valuename (宣言した)変数の名前
    get_content() -> 宣言の具体的な内容
    関数の宣言は代入とセットの場合がある
    """
    def __init__(self,mutable:str, valuename: str, type_:str, contents:list, depth:int, loopdepth: int, pub_flag = False) -> None:
        super().__init__(
            valuename, # 宣言した変数(または定数)名
            contents,   # 初期化式、Noneの場合もある
            depth,
            loopdepth
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
        return f"\n{'    ' * self.depth}<{type(self).__name__} depth:({self.depth}) pubflag:({self.pub_flag}) {self.mutable} value_name:({self.name}) value_type({self.type_}) contents:({self.contents})>"

    def get_all_local_value(self):
        rlist:list = list()
        if self.contents is not None:
            for i in self.contents:
                local_value = i.get_all_local_value()
                rlist += local_value
        rlist += [copy.copy(self)]
        return rlist

    def wat_format_gen(self) -> str:
        """
        watに変換したら完全に変数宣言の部分と代入部分が分離するので
        ここでは、代入の処理変換するだけでよい
        TODO: いまはまだi32のみの対応で良い
        ```wat
        ;; 宣言済みの変数$aに10を代入する例
        i32.const 10
        local.set $a
        ```
        """
        wasm_code = ""
        if self.contents:
            #
            wasm_code += self.contents[0].wat_format_gen()
            wasm_code += "local.set ${}\n".format(self.name)
        else:
            # 変数の宣言のみで、代入部分が存在しないばあいはpass
            pass
        return wasm_code

class Expr(Elem): # Exprは一時的なものである
    """
    # Expr
    式を一時的にまとめておく場所です
    ## returns
    get_contents() -> <expr>
    """
    def __init__(self, name: str, contents: list, depth:int, loopdepth: int) -> None:
        super().__init__(name, contents, depth, loopdepth)

    def resolve_self(self):
        """
        # resolve_self
        """
        expr_parser = Expr_parser(self.contents,depth = self.depth)
        self.contents = expr_parser.resolve()

    def __repr__(self):
        return f"\n{'    ' * self.depth}<{type(self).__name__} depth:({self.depth}) expr:({self.contents})>"

    def get_all_local_value(self):
        rlist:list = list()
        for i in self.contents:
            local_value = i.get_all_local_value()
            rlist += local_value
        return rlist

    def wat_format_gen(self) -> str:
        wasm_code = ""
        if self.contents:
            wasm_code += self.contents[0].wat_format_gen()
        else:
            # self.contentsがからである場合
            pass
        return wasm_code

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
    def __init__(self, name: str, expr: str, depth:int, loopdepth: int) -> None:
        super().__init__(name, expr, depth, loopdepth)

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
        wasm_code = ""
        for i in self.contents:
            wasm_code += i[0].wat_format_gen()
        
        #
        if self.name == "return":
            wasm_code += "return\n"
        elif self.name == "break":
            wasm_code += "br $#block{}\n".format(self.loopdepth - 1)
        elif self.name == "continue":
            wasm_code += "br $#loop{}\n".format(self.loopdepth - 1)
        elif self.name == "assert":
            pass
        else:
            raise BaseException("Error!")
        return wasm_code

    def resolve_self(self):
        #print(self.contents)
        expr_parser = Parser(self.contents, depth = self.depth + 1)
        self.contents = expr_parser.resolve()
        self.contents = [Expr_parser(i,depth=self.depth+1).resolve() for i in self.contents]
    
    def get_all_local_value(self):
        rlist:list = list()
        for i in self.contents:
            local_value = i[0].get_all_local_value()
            rlist += local_value
        return rlist


# Type_Elem
class Type_Elem(Elem):
    """
    # Type_Elem
    タイプ宣言用
    """
    def __init__(self, name: str, contents: str) -> None:
        self.primitive_type = [
            "i32",
            "i64",
            "f32",
            "f64"
        ]

        super().__init__(name, contents,None,None)


class TypeBlock(Type_Elem):
    """
    # TypeBlock
    ## synatax
    Vec<T,T>
    ## interpret as
    name = "Vec"
    contents = [<type>,<type>]
    """
    def __init__(self, name: str, contents: list) -> None:
        # depth:void 
        # loopdepth:void
        # blockをまとめるときのダミーの引数
        super().__init__(name, contents, None, None)

    def resolve_self(self):
        """
        # resolve_self 
        self.contentsのそれぞれの要素はタイプ型
        TODO
        """
        pass

class TypeTuple(Type_Elem):
    """
    # Type_tuple
    ## syantax
    (T, T, T)
    ## interpret as
    name = None
    contents = [<type>,<type>]
    """
    def __init__(self, name: str, contents: list) -> None:
        super().__init__(name, contents)

    def resolve_self(self):
        """
        # 
        TODO
        """
        pass

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

class Type_char(Type_Elem):
    """
    # Type_char

    """
    def __init__(self, name: str, contents: str) -> None:
        super().__init__(name, contents)

# 特別なType
class Type_Mat(Type_Elem):
    """
    # Type_Mat
    ## format
    MatNxM<T>
    ## as
    array
    """
    def __init__(self, name: str, contents: str) -> None:
        super().__init__(name, contents)

class Type_Vec(Type_Elem):
    """
    # Type_Vec
    ## format
    VecN<T>
    """
    def __init__(self, name: str, contents: str) -> None:
        super().__init__(name, contents)

class Type_List(Type_Elem):
    def __init__(self, name: str, contents: str) -> None:
        super().__init__(name, contents)
