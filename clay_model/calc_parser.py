from enum import Enum,auto

# debug tools
from pprint import pprint
import logging

logging.basicConfig(level=logging.DEBUG)


class func:

    def __init__(self,funccode:str):
        self.code:str=funccode
        funcname, funcargs=self.split()
        self.funcname=self.check_funcname(funcname)
        if " " in self.funcname:
            raise BaseException("関数名に半角スペースを入れないでください")
        self.funcargs=self.split_args(funcargs)

    @classmethod
    def new(cls,code:str):return func(code)

    def check_funcname(self,text:str) -> str:
        #funcname内の文字列がすべて有効かどうかを調べる関数
        if text[0]==" ":#半角スペースが文字列の前に入っていた場合
            return self.check_funcname(text[1:])
        if text[-1]==" ":
            return self.check_funcname(text[:-1])
        return text

    def split(self) -> tuple[str,str]:
        index = self.code.find("(")
        if index<0:
            raise BaseException("引数部分の文法が不正だと思われます。おそらく")
        else:
            funcname:str = self.code[:index]
            funcargs:str = self.code[index:]
        return funcname,funcargs

    def split_args(self,funcargs):
        #引数を抽出する
        depth:int = 0
        args:list[str] = []
        arg:str = ""
        for i in funcargs:
            match i:
                case "(":
                    if depth > 0:
                        arg += i
                    depth += 1
                case ")":
                    depth -= 1
                    if depth > 0:
                        arg += i
                case _:
                    if depth > 1:
                        arg += i
                    else:
                        if i == ",":
                            args.append(arg)
                            arg = ""
                        else:
                            arg += i
        if arg:
            args.append(arg)
        return args

    @property
    def data(self):
        funcname,funcargs = self.split()
        funcname = self.check_funcname(funcname)
        return [funcname] + self.split_args(funcargs)

    def __repr__(self) -> str:
        return f"name:'{self.funcname}'\nargs:{self.funcargs}"


class brackets:

    def __init__(self,bracketscode:str):
        self.code:str = bracketscode

    @classmethod
    def new(cls,code):return brackets(code)

    def __inner_content(self,code:str):
        depth:int=0
        rlist:list[str] = list()
        for i in code:
            match i:
                case "(":
                    if depth > 0:rlist.append(i)
                    depth += 1
                case ")":
                    depth -= 1
                    if depth > 0:rlist.append(i)
                case _:
                    if depth > 0:rlist.append(i)
        rtext = "".join(rlist)
        return self.__inner_content(rtext) if elem.new(rtext).elemtype is Elem_type.BRACKETS else rtext

    @property
    def inner(self) -> str:
        return self.__inner_content(self.code)


class value:

    def __init__(self,code:str):
        self.code:str = self.check_valuename(code)
        if " " in self.code:
            raise BaseException("半角スペースが入っています")

    @classmethod
    def new(cls,code:str):return value(code)

    def check_valuename(self,valuename:str) -> str:
        if valuename[0] == " ":
            return self.check_valuename(valuename[1:])
        if valuename[-1] == " ":
            return self.check_valuename(valuename[:-1])
        return valuename

    @property
    def inner(self):
        return self.code


class Elem_type(Enum):
    #type of elem
    FUNCTION  = auto()
    OPERATION = auto()
    NUMBER    = auto()
    BRACKETS  = auto()
    OTHER     = auto()
    VALUE     = auto()
    FORMULA   = auto()


class elem:

    #式のelement
    def __init__(self,code):
        """

        """
        self.availablechars:list[str] = [
                chr(i) for i in range(65,65+26)#A~Z
        ]+[
                chr(i) for i in range(97,97+26)#a~z
        ]+[
                str(i) for i in range(10)      #0~9
        ]
        self.code = code

    @classmethod
    def new(cls,code):return elem(code)

    #bool
    def __is_FUNCTION(self,code:str) -> bool:#工事中
        index = code.find("(")
        if index < 0:
            return False
        else:
            funcname:str = code[:index]
            funcargs:str = code[index:]
            #本当はここに関数名が正しく設定されているかを確認する関数を作成したい
            if self.__is_BRACKETS(funcargs):
                return True
            else:
                return False

    def __is_BRACKETS(self,code:str) -> bool:
        group:list[bool] = []
        depth:int = 0
        for i in code:
            match i:
                case "(":
                    depth += 1
                    group.append(depth > 0)
                case ")":
                    group.append(depth > 0)
                    depth -= 1
                case " ":
                    pass
                case _:
                    group.append(depth > 0)
        return all(group)

    def __is_NUMBER(self,code:str) -> bool:
        #⚠️少数点の場合も含む
        #アンダースコアは許容しない(とりあえずは。。。)
        group:list[str] = []
        space_flag = False
        end_flag = False
        nums:list[str] = list(map(str,range(10)))#1~10の数字のリスト
        for i in code:
            if (i in nums) and end_flag == False:
                group.append(i)
                end_flag = True
            elif i == ".":
                if group:
                    group.append(i)
                else:
                    raise BaseException("小数点が先頭についてしまっていますよ")
            elif i == " " and space_flag == False:
                pass
            elif i == " " and space_flag == True:
                end_flag = True
            else:
                return False

        return True

    def __is_OPERATION(self,code:str) -> bool:
        opelist:list[str] = ["+","-","*","/","%","^","@"]
        for i in opelist:
            if i == code:
                return True
        return False

    def __is_VALUE(self,code:str) -> bool:
        for i in code:
            if i in self.availablechars:
                pass
            elif i==" ":
                pass
            else:
                return False
        return True

    def __is_FORMULA(self,code:str) -> bool:
        depth:int = 0
        for i in code:
            match i:
                case "(":
                    depth += 1
                case ")":
                    depth -= 1
                case _:
                    if depth > 0:
                        pass
                    else:
                        if i in ["+","-","*","/","%","^","@"]:
                            return True
        return False

    def __is_control(self,code:str) -> bool:
        pass

    @property
    def elemtype(self) -> Elem_type:
        if self.__is_OPERATION(self.code):
            return Elem_type.OPERATION
        elif self.__is_NUMBER(self.code):
            return Elem_type.NUMBER
        elif self.__is_BRACKETS(self.code):
            return Elem_type.BRACKETS
        elif self.__is_FORMULA(self.code):
            return Elem_type.FORMULA
        elif self.__is_FUNCTION(self.code):
            return Elem_type.FUNCTION
        elif self.__is_VALUE(self.code):
            return Elem_type.VALUE
        else:
            return Elem_type.OTHER


class parser:

    def __init__(self,code:str,mode = "lisp"):
        self.code:str = code
        self.mode = mode
        self.availablechars:list[str]=[
                chr(i) for i in range(65, 65 + 26)#A~Z
        ]+[
                chr(i) for i in range(97, 97 + 26)#a~z
        ]+[
                str(i) for i in range(10)      #0~9
        ]
        # <, <=, >, >=, !=,
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
        self.length_order = sorted(self.rankinglist.keys(),key=lambda a:len(a))[::-1]

    def grouping_number(self,vec:str) -> list[str]:
        # numberをまとめる
        rlist:list[str] = list()
        group:list[str] = list()
        flag:bool = False
        for i in vec:
            if i in self.availablechars:
                group.append(i)
                flag = True
            else:
                if flag:
                    rlist.append("".join(group))
                    group = []
                    flag = False
                rlist.append(i)
        if flag:
            rlist.append("".join(group))
        return rlist

    def grouping_brackets(self,vec:list[str]) -> list[str]:
        # functionをまとめる
        rlist:list[str] = list()
        group:list[str] = list()
        depth:int = 0
        flag:bool = False
        for i in vec:
            match i:
                case "(":
                    if depth > 0:
                        group.append(i)
                    elif depth == 0:
                        group.append(i)
                        flag = True
                    else:
                        raise BaseException("括弧を閉じ忘れている可能性があります")
                    depth += 1
                case ")":
                    depth -= 1
                    if depth > 0:
                        group.append(i)
                    elif depth == 0:
                        group.append(i)
                        rlist.append("".join(group))
                        group = []
                        flag = False
                    else:
                        raise BaseException("括弧を開き過ぎている可能性があります")
                case _:
                    if flag:
                        group.append(i)
                    else:
                        rlist.append(i)
        return rlist

    def is_symbol(self,index:int,vec:list) -> tuple[bool,str,int]:
        # (is_match? :bool, string:str, step:int)
        # マッチしたかに関わらずsplit文字に応じたstepを返却する
        size = len(vec)
        for string in self.length_order:# self.length_oerderは長い順に並んだ配列
            for i,char in enumerate(string): 
                if 0 <= index+i < size and vec[index+i]!=char:
                    break
            else:
                return (True, string, len(string))
        return (False, None, 1)

    def split_symbol(self,vec:list[str]) -> list[str]:
        rlist:list[str] = list()
        group:list[str] = list()

        i = 0
        size = len(vec)
        while (i < size):
            is_match, ope_string, step = self.is_symbol(i,vec)
            if is_match:
                if group:
                    rlist.append("".join(group))
                    group = list()
                rlist.append(ope_string)
            else:
                group.append(vec[i])
            i+=step
        if group:
            rlist.append("".join(group))
        return rlist

    def code2vec(self) -> list[str]:
        vec = self.grouping_number(self.code)
        vec = self.grouping_brackets(vec)
        vec = self.split_symbol(vec)
        return vec

    def resolve_operation(self,code:str) -> "formula_tree":
        #逆ポーランド記法の返り値
        #引数が二つであると決定した
        par = parser(code)
        vec = par.code2vec()
        index = self.priority(vec)
        if index is None:
            return code
        E1:str = "".join(vec[:index])
        ope = vec[index]
        E2:str = "".join(vec[index+1:])
        return formula_tree(
                ope,
                Elem_type.OPERATION,
                [*self.resolve_util(E1),*self.resolve_util(E2)],
                self.mode
            )

    def resolve_util(self,E):
        elem_type = elem.new(E).elemtype
        if elem_type   is Elem_type.FORMULA:  return self.resolve_operation(E),
        elif elem_type is Elem_type.BRACKETS: return self.resolve_operation(brackets.new(E).inner),
        elif elem_type is Elem_type.FUNCTION: return self.resolve_function(E),
        elif elem_type is Elem_type.VALUE:    return value.new(E).inner,
        else :                                return E,        

    def resolve_function(self,code:str) -> "formula_tree":
        funcdata = func.new(code).data
        funcname=funcdata[0]
        return formula_tree(
            funcname,
            Elem_type.FUNCTION,
            [self.resolve_util(i)[0] for i in funcdata[1:]],
            mode = self.mode
        )

    def resolve(self) -> "formula_tree":
        return self.resolve_util(self.code)[0]

    def priority(self,vec:list[str]) -> int|None:
        #配列内にある最も優先順位が低い演算子を探します
        #返り値はindexです
        """
        実装されている計算規則
        rankの数字が低いものほど計算順位も低い
        同一のランクが並列に続く場合、式の右に行く程計算順位が低い
        """
        rank:int = 3
        index = None
        for i,j in enumerate(vec):
            if j in self.rankinglist.keys():
                if rank > self.rankinglist[j]:
                    rank = self.rankinglist[j]
                    index = i
                elif rank == self.rankinglist[j]:
                    # 右に計算順位が同じ演算子を見つけた場合
                    # 右にあるものの方が計算順位が低い
                    rank = self.rankinglist[j]
                    index = i
        # 最も計算順位が1番低いindexを返す
        return index


class formula_tree:

    # mode : lisp(RPM)|PM|wat(wasm)
    def __init__(self,name:str,type_:Elem_type,args:list,mode="lisp"):
        self.mode = mode
        self.name:str = self.ope2func(name)
        self.args:list = args
        self.selftype:Elem_type=type_

    def ope2func(self,name:str) -> str:
        """
        演算子を関数のように見る
        """
        match name:
            case "+":
                return "+"
            case "-":
                return "-"
            case "*":
                return "*"
            case "/":
                return "/"
            case "%":
                return "%"
            case "@":
                return "@"
            case _:
                return name

    def __getitem__(self,key):
        return self.args[key]

    def __repr__(self):

        if self.mode == "lisp" or self.mode == "RPM":
            return f"({self.name} {' '.join(map(lambda a:str(a) if type(a) is str else repr(a),self.args))})"
        elif self.mode == "PM":
            return f"({' '.join(map(repr,self.args))} {self.name})"
        return f"({' '.join(map(repr,self.args))} {self.name})"


## Wat Tools


class Wat_data_type(Enum):
    I32 = auto()
    I64 = auto()
    F32 = auto()
    F64 = auto()


class Wat_role(Enum):
    CONST = auto()
    VALUE = auto()
    OPE   = auto()


class tree2wat:
    # parserで変換した後のtreeデータに対して処理を施します

    def __init__(self,tree:formula_tree ,data_type = Wat_data_type.I32):
        #
        self.data_type = data_type

        # 
        self.tree = tree
        self.ope_dict = {
            "+" : "add",
            "-" : "sub",
            "*" : "mul",
            "/" : "div",
            "%" : "rem_u",
        }
        self.stack:list = []

    def is_num(self,text:str):
        for i in text:
            if '0' <= i <= '9' or i == "." or i == " ":
                pass
            else:
                return False
        return True

    # wat形式のsukuriputoを出力する
    def gen_code(self) -> list:
        self.gen_code_rec(self.tree)
        return self.stack

    def gen_code_rec(self, parent:formula_tree):
        if type(parent) is str:
            if self.is_num(parent):
                self.stack.append((Wat_role.CONST, parent))
            else:
                self.stack.append((Wat_role.VALUE, parent))
        else:
            for i in parent.args:
                self.gen_code_rec(i)
            self.stack.append((Wat_role.OPE, parent.name))

    def type_str(self):
        match self.data_type:
            case Wat_data_type.I32:
                return"i32"
            case Wat_data_type.I64:
                return"i64"
            case Wat_data_type.F32:
                return"f32"
            case Wat_data_type.F64:
                return"f64"

    def ope_resolve(self,ope_name:str):
        if ope_name in self.ope_dict:
            return '.'.join([self.type_str(), self.ope_dict[ope_name]])
        else:
            return ' '.join(["call", '$'+ope_name])

    def role_conv(self, a0:Wat_role, a1:str) -> str:
        match a0:
            case Wat_role.CONST:
                return '.'.join([self.type_str(), "const"]) + ' ' + a1
            case Wat_role.VALUE:
                return '.'.join(["local", "get"]) + ' ' + '$' + a1
            case Wat_role.OPE:
                return self.ope_resolve(a1)
            case _:
                BaseException("Error!")

    def conv2wat(self, stack_data:list):
        rdata:str = ""
        for i in stack_data:
            rdata += self.role_conv(i[0], i[1])
            rdata += '\n'
        return rdata


## test functions

def __test_00():
    texts=[
    " 10 + ( x + log10(2) * sin(x) ) * log10(x)",
    "(-sin(x)*3)+(-2*cos(x))",
    "pi",
    "sin(x)",
    "(1)+2",
    "3.14",
    "-8+6",
    "a / b*(c+d)",
    "a / (b*(c+d))",
    "a*a*a",
    "x^3+x^2+3",
    "2*cube(x)+3*squared(x)+3"
    ]
    """
    texts = [
        "f(x)+g(x,y,z)*5"
    ]
    """
    for i in texts:
        par=parser(i,mode="PM")
        print("resolve",par.resolve())
    el = elem("-sin(x)")
    print(el.elemtype)
    #print(
    #    elem.new(" sin(x) ").elemtype
    #)

def __test_01():
    #par = parser("gcd(b,a % b)",mode="PM")
    # 空文字は 0 として扱う
    par = parser("sqrt(pow(a, 2), pow(b, 2))",mode="lisp")
    #par = parser("pow(a+b,n)",mode="lisp")
    tree = par.resolve()
    wat_conv = tree2wat(tree)
    stack = wat_conv.gen_code()
    print(tree)
    pprint(stack)
    print(wat_conv.conv2wat(stack))

def __test_02():
    #par = parser("gcd(b,a % b)",mode="PM")
    # 空文字は 0 として扱う
    #par = parser("10 ** 20",mode="lisp")
    #par = parser("sqrt(pow(value1 , 1 + 1) + pow(value2 , 2))",mode="lisp")
    #par = parser("pow(a+b,n)",mode="lisp")
    par = parser("abc + b * c ++ gcd(a+b,b)",mode="lisp")
    tree = par.resolve()
    wat_conv = tree2wat(tree)
    stack = wat_conv.gen_code()
    print(tree)
    # pprint(stack)
    print(wat_conv.conv2wat(stack))

def __test_03():
    test_case=[
        "x**2 + y**2 == 1",
        "1==x**2+y**2",
        "gcd(b,a % b)",
        "sqrt(x**2+y**2)",
        "1+1+1 == -(1+1)",
        "0< index + i <= size"
    ]
    for i in test_case:
        par:parser = parser(i,mode="PM")
        tree:formula_tree = par.resolve()
        wat_conv = tree2wat(tree)
        stack = wat_conv.gen_code()
        print(i,tree)
        # pprint(stack)
        # print(wat_conv.conv2wat(stack))


if __name__ == "__main__":
    # __test_00()
    # __test_01()
    __test_03()