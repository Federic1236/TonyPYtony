import sys
import os
import re
import importlib
from colorama import Fore, Style, init

init(autoreset=True)

class AIWrapper:
    def __init__(self, provider, client=None):
        self.provider = provider
        self.client = client

    def genera(self, prompt, **kwargs):
        if self.provider == "openai":
            try:
                if hasattr(self.client, "ChatCompletion"):
                    resp = self.client.ChatCompletion.create(model=kwargs.get("model","gpt-3.5-turbo"), messages=[{"role":"user","content":prompt}])
                    return resp.choices[0].message.content if hasattr(resp.choices[0], "message") else resp.choices[0].text
                else:
                    resp = self.client.Completion.create(engine=kwargs.get("model","text-davinci-003"), prompt=prompt, max_tokens=kwargs.get("max_tokens",150))
                    return resp.choices[0].text
            except Exception as e:
                return f"[AI error] {e}"
        if self.provider in ("local", "local_hf"):
            # local HF model if available, otherwise a tiny fallback
            if self.provider == "local_hf" and self.client is not None:
                try:
                    pipe = self.client  # already a pipeline
                    out = pipe(prompt, max_length=kwargs.get("max_length", 150), num_return_sequences=1)
                    if isinstance(out, list) and isinstance(out[0], dict):
                        return out[0].get("generated_text", str(out[0]))
                    return str(out)
                except Exception as e:
                    return f"[Local HF error] {e}"
            # Very small fallback generator (no external models)
            import random, re
            s = re.sub(r'\s+', ' ', prompt.strip())
            canned = [
                "Interessante. Dimmi di più su",
                "Capisco. Riguardo a",
                "Ecco un'idea su",
                "Non sono sicuro, ma potrei suggerire"
            ]
            return random.choice(canned) + " " + (s if len(s) < 200 else s[:200] + "...")
        return f"[Unsupported AI provider: {self.provider}]"

class TonyPytony:
    def __init__(self):
        self.variables = {}
        self.aliases = {}  # map tony name -> python variable name or dotted path

    def report_error(self, message, line_no=None, line_content=None):
        prefix = f"Line {line_no}: " if line_no is not None else ""
        line_info = f" -> {line_content.strip()}" if line_content else ""
        print(f"{Fore.RED}{Style.BRIGHT}{prefix}{message}{line_info}")

    def run_line(self, line, line_no=None):
        raw = line
        line = line.strip()
        if not line or line.startswith("//"):
            return

        try:
            if line.startswith("urla "):
                content = line[5:].strip()
                value = self.evaluate_expression(content, line_no, raw)
                if value is None:
                    return
                print(f"{Fore.CYAN}{Style.BRIGHT}{value}")

            elif line.startswith("bomboroide "):
                match = re.match(r"bomboroide\s+([A-Za-z_]\w*)\s*=\s*(.+)", line)
                if match:
                    var_name, var_expr = match.groups()
                    value = self.evaluate_expression(var_expr.strip(), line_no, raw)
                    if value is not None:
                        self.variables[var_name.strip()] = value
                else:
                    self.report_error("Syntax error in 'bomboroide' (expected: bomboroide name = expr)", line_no, raw)

            elif line.startswith("usa_tutto"):
                # try importing a curated list of stdlib and common packages
                modules = [
                    "sys","os","re","math","json","time","datetime","itertools","functools","random",
                    "threading","subprocess","typing","pathlib","collections","http","urllib",
                    "numpy","pandas","requests","flask","torch","transformers"
                ]
                for m in modules:
                    try:
                        mod = importlib.import_module(m)
                        short = m.split(".")[-1]
                        self.variables[short] = mod
                    except Exception:
                        continue

            elif line.startswith("usa "):
                # usa <module.name> [as alias]
                m = re.match(r"usa\s+([A-Za-z0-9_.]+)(?:\s+as\s+([A-Za-z_]\w*))?$", line)
                if m:
                    module_name, alias = m.groups()
                    try:
                        mod = importlib.import_module(module_name)
                        varname = alias or module_name.split(".")[-1]
                        self.variables[varname] = mod
                    except Exception as e:
                        self.report_error(f"Import error: {e}", line_no, raw)
                else:
                    self.report_error("Syntax error in 'usa' (expected: usa module.name [as alias])", line_no, raw)

            elif line.startswith("alias "):
                # alias name = expression   (bind a Tony name to a python object/value)
                m = re.match(r"alias\s+([A-Za-z_]\w*)\s*=\s*(.+)", line)
                if m:
                    name, expr = m.groups()
                    val = self.evaluate_expression(expr.strip(), line_no, raw)
                    if val is not None:
                        # if val is a string representing dotted path, store as alias to resolve later
                        if isinstance(val, str) and "." in val and val in self.variables:
                            self.aliases[name] = val
                        else:
                            self.variables[name] = val
                else:
                    self.report_error("Syntax error in 'alias' (expected: alias name = expression)", line_no, raw)

            elif line.startswith("crea_ai "):
                # crea_ai name provider [api_key_var] [model_name]
                m = re.match(r"crea_ai\s+([A-Za-z_]\w*)\s+([A-Za-z_]\w*)(?:\s+([A-Za-z_]\w*))?(?:\s+(.+))?$", line)
                if m:
                    name, provider, keyvar, modelname = m.groups()
                    provider = provider.lower()
                    if provider == "openai":
                        try:
                            openai = importlib.import_module("openai")
                            if keyvar and keyvar in self.variables:
                                openai.api_key = self.variables[keyvar]
                            elif os.environ.get("OPENAI_API_KEY"):
                                openai.api_key = os.environ.get("OPENAI_API_KEY")
                            self.variables[name] = AIWrapper("openai", client=openai)
                        except Exception as e:
                            self.report_error(f"Failed to initialize OpenAI client: {e}", line_no, raw)
                    elif provider in ("local", "local_hf"):
                        if provider == "local_hf":
                            # try to create a transformers pipeline for local generation
                            try:
                                transformers = importlib.import_module("transformers")
                                model = (modelname or "gpt2").strip()
                                pipe = transformers.pipeline("text-generation", model=model, device=-1)
                                self.variables[name] = AIWrapper("local_hf", client=pipe)
                            except Exception as e:
                                self.report_error(f"Failed to initialize local HF model: {e}", line_no, raw)
                                self.variables[name] = AIWrapper("local")
                        else:
                            self.variables[name] = AIWrapper("local")
                    else:
                        self.report_error("Unsupported AI provider (supported: openai, local, local_hf)", line_no, raw)
                else:
                    self.report_error("Syntax error in 'crea_ai' (expected: crea_ai name provider [api_key_var] [model])", line_no, raw)

            else:
                # fallback: try evaluating as expression / function call / attribute access
                result = self.evaluate_expression(line, line_no, raw)
                if result is not None and not callable(result):
                    print(f"{Fore.GREEN}{result}")

        except Exception as e:
            self.report_error(f"Unhandled exception: {e}", line_no, raw)

    def resolve_dotted(self, dotted, line_no=None, line_content=None):
        # resolve aliases first
        if dotted in self.aliases:
            dotted = self.aliases[dotted]
        parts = dotted.split(".")
        if parts[0] not in self.variables:
            self.report_error(f"Undefined variable or module: '{parts[0]}'", line_no, line_content)
            return None
        obj = self.variables[parts[0]]
        for attr in parts[1:]:
            try:
                obj = getattr(obj, attr)
            except Exception as e:
                self.report_error(f"Attribute error: {e}", line_no, line_content)
                return None
        return obj

    def get_value(self, token, line_no=None, line_content=None):
        token = token.strip()
        # string literal
        if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
            return token[1:-1]
        # numeric literal (int or float)
        if re.fullmatch(r"[+-]?\d+(\.\d+)?", token):
            return int(token) if "." not in token else float(token)
        # boolean/null literals
        if token in ("True","False","None"):
            return {"True":True,"False":False,"None":None}[token]
        # dotted attribute/module access
        if "." in token:
            return self.resolve_dotted(token, line_no, line_content)
        # variable lookup
        if token in self.variables:
            return self.variables[token]
        # raw python builtin names mapped via aliases
        if token in self.aliases and self.aliases[token] in self.variables:
            return self.variables[self.aliases[token]]
        # unknown token
        self.report_error(f"Undefined variable or invalid token: '{token}'", line_no, line_content)
        return None

    def evaluate_expression(self, expr, line_no=None, line_content=None):
        expr = expr.strip()
        # movimento operator
        if " movimento " in expr:
            parts = expr.split(" movimento ", 1)
            left = self.get_value(parts[0], line_no, line_content)
            right = self.get_value(parts[1], line_no, line_content)
            if left is None or right is None:
                return None
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            return str(left) + str(right)

        # function call: name(...) possibly dotted
        m = re.match(r"^([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*\((.*)\)\s*$", expr)
        if m:
            target, raw_args = m.groups()
            args = [a.strip() for a in raw_args.split(",")] if raw_args.strip() else []
            resolved_args = [self.get_value(a, line_no, line_content) for a in args]
            if any(a is None for a in resolved_args):
                return None
            # resolve callable
            if "." in target:
                func = self.resolve_dotted(target, line_no, line_content)
            else:
                # support aliases names pointing to dotted paths or objects
                if target in self.aliases:
                    alias_target = self.aliases[target]
                    func = self.resolve_dotted(alias_target, line_no, line_content) if "." in alias_target else self.variables.get(alias_target)
                else:
                    func = self.variables.get(target)
            if not callable(func):
                self.report_error(f"Target is not callable: '{target}'", line_no, line_content)
                return None
            try:
                return func(*resolved_args)
            except Exception as e:
                self.report_error(f"Error while calling '{target}': {e}", line_no, line_content)
                return None

        # fallback to value lookup
        return self.get_value(expr, line_no, line_content)

def main():
    if len(sys.argv) < 2:
        print("TonyPytony Engine: No file specified.")
        return

    target_file = os.path.abspath(sys.argv[1])
    if not os.path.exists(target_file):
        print(f"File not found: {target_file}")
        return

    interpreter = TonyPytony()
    try:
        with open(target_file, "r", encoding="utf-8") as file:
            for idx, line in enumerate(file, start=1):
                interpreter.run_line(line, idx)
    except Exception as e:
        print(f"{Fore.RED}Fatal error while reading file: {e}")

if __name__ == "__main__":
    main()
