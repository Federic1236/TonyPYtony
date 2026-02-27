import sys
import os
import re
from colorama import Fore, Style, init

init(autoreset=True)

class TonyPytony:
    def __init__(self):
        self.variables = {}

    def run_line(self, line):
        line = line.strip()
        if not line or line.startswith("//"):
            return

        if line.startswith("urla "):
            content = line[5:].strip()
            print(f"{Fore.CYAN}{Style.BRIGHT}{self.get_value(content)}")

        elif line.startswith("bomboroide "):
            match = re.match(r"bomboroide (.+) = (.+)", line)
            if match:
                var_name, var_expr = match.groups()
                self.variables[var_name.strip()] = self.evaluate_expression(var_expr.strip())

    def get_value(self, token):
        token = token.strip()
        if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
            return token[1:-1]
        if token.isdigit():
            return int(token)
        return self.variables.get(token, token)

    def evaluate_expression(self, expr):
        if " movimento " in expr:
            parts = expr.split(" movimento ")
            return str(self.get_value(parts[0])) + str(self.get_value(parts[1]))
        return self.get_value(expr)

def main():
    if len(sys.argv) < 2:
        print("TonyPytony Engine: No file specified.")
        return

    target_file = os.path.abspath(sys.argv[1])
    if not os.path.exists(target_file):
        print(f"File not found: {target_file}")
        return

    interpreter = TonyPytony()
    with open(target_file, "r", encoding="utf-8") as file:
        for line in file:
            interpreter.run_line(line)

if __name__ == "__main__":
    main()