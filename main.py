import os
import re
import sys
import ast
import colorama as col
from transpiler import PythonToJavascript

def buildSource(target_file: str):
    code = None
    with open(target_file, "r") as f1:
        code = ast.parse(f1.read())
    build_ast = PythonToJavascript()
    build_ast.visit(code)
    return build_ast

def main():
    if len(sys.argv) == 1:
        print(f"{col.Fore.CYAN}Convert your python source file, into Javascript.{col.Fore.WHITE}")
        print(f"{col.Fore.YELLOW}Performs Syntax Translation only!")
        print("Use `--help` command")
        os._exit(0)
    elif sys.argv[1] == "--help":
        print(f"{col.Fore.CYAN} `command target_py_file -o target_js_file`{col.Fore.GREEN} output js file")
        print(f"{col.Fore.CYAN} `command target_py_file` {col.Fore.GREEN} display js source!{col.Fore.WHITE}`")
        os._exit(0)
    target_file = sys.argv[1]
    output_file = None
    if len(sys.argv) > 2:
        if sys.argv[2] == "-o":
            if len(sys.argv) < 4:
                print(f"{col.Fore.RED}ERROR{col.Fore.RED}Please provide an input file!")
                os._exit(1)
            output_file = sys.argv[3]
    if not os.path.exists(target_file):
        print(f"{col.Fore.RED}ERROR:{col.Fore.WHITE} the input file doesn't exist!")
        os._exit(1)
    if re.search(r"\.py", target_file) is None:
        print(f"{col.Fore.RED}ERROR:{col.Fore.WHITE} the input file must be a python file!")
        os._exit(1)
    source = buildSource(target_file)
    if output_file != None:
        print("File created!")
        with open(output_file, "w") as f1:
            f1.write(source.target_lang)
        os._exit(0)
    print(source.target_lang)

if __name__ == "__main__":
    main()

