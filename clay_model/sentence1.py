from enum import Enum,auto

class Object_type(Enum):
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


class proc_parser:
    def __init__(self, code:str) -> None:
        self.code=code

    def proc_resolve(self,code:str):
        # 処理部の文法解釈
        pass

    def resolve0(self):
        pass

    def resolve1(self):
        pass

    def resolve_quatation(self):
        
        # クォーテーションをまとめる
        pass

    def group_block(self):
        pass


class proc_tree:
    def __init__(self,) -> None:
        pass
    
    