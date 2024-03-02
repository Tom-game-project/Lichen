import ast

# "-1**2"
# "(-1)**2"

src = [
    "-1**-1**-1",
    "-1*-2*-3",
    "-1-2-3",
    "1+2+3"
]

# srcをASTに変換
parsed_src = ast.parse(src[2])

# ターミナル出力
print(ast.dump(parsed_src, indent=4))