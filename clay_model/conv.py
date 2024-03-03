"""
# conv.py
## convert lichen to wasm text format
"""
import parser

class lc2wat_compiler:
    """
    # wasm_compiler 
    ## lichen をwasmにコンパイルします
    """
    def __init__(self,codelist:list["parser.Elem"]):
        self.module = "(module {0})"
        self.func = "func {0}"
        self.code:list["parser.Elem"] = codelist

        # wasm setting
        self.num_t = [
            "i32",
            "i64",
            "f32",
            "f64",
        ]
        self.ope_table = {
            "+":"add",
            "-":"sub",
            "*":"mul",
            "+":"div_u",
            "%":"rem_u",
        }

    def lc2wat(self):
        pass