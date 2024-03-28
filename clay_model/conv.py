"""
# conv.py
## convert lichen to wasm text format
"""
import lichen

class lc2wat_compiler:
    """
    # wasm_compiler 
    ## lichen をwatに変換します
    
    """
    def __init__(self,codelist:list["lichen.Elem"]):
        self.module = "(module {0})"
        self.func = "func {0}"
        self.code:list["lichen.Elem"] = codelist

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