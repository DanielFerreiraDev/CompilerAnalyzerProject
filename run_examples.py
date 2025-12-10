import os, json
from parser import Parser, ParseError

EX_DIR = "examples"
OUT_DIR = "outputs"
os.makedirs(OUT_DIR, exist_ok=True)

for fn in sorted(os.listdir(EX_DIR)):
    if fn.endswith(".c"):
        text = open(os.path.join(EX_DIR, fn)).read()
        try:
            p = Parser(text)
            ast = p.parse()
            open(os.path.join(OUT_DIR, fn + ".ast.json"), "w").write(json.dumps(ast.to_dict(), indent=2))
            print("Parsed", fn, "-> OK")
        except Exception as e:
            open(os.path.join(OUT_DIR, fn + ".error.txt"), "w").write(str(e))
            print("Parsed", fn, "-> ERROR:", e)
